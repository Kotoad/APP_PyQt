"""
============================================================
  3D WIRING SYSTEM  —  PyQt6 + OpenGL
============================================================

WHAT THIS DOES:
  Renders an interactive 3D scene with nodes (spheres) connected
  by curved wires (Bezier tubes). You can orbit, pan, zoom and
  click to select nodes.

INSTALL (run once in your terminal):
  pip install PyQt6 PyOpenGL PyOpenGL-accelerate numpy pyrr

CONTROLS:
  Left-drag    → orbit camera
  Middle-drag  → pan camera
  Scroll       → zoom in / out
  Left-click   → select a node (turns cyan)
  A key        → add a new random node
  W key        → connect last two selected nodes with a wire
  Delete       → remove selected node and its wires
  R key        → reset camera
  ESC          → quit

RUN:
  python wire3d.py

============================================================
"""

# ──────────────────────────────────────────────────────────
# IMPORTS
# ──────────────────────────────────────────────────────────

import sys          # for sys.exit()
import ctypes       # for byte-offset pointers in OpenGL calls
import random       # for random node placement
from dataclasses import dataclass, field
from typing import List, Optional, Dict

import numpy as np  # all our math lives in numpy arrays

# PyQt6: the window, event loop, and OpenGL widget
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtGui import QSurfaceFormat, QFont, QColor
from PyQt6.QtCore import Qt, QTimer

# pyrr: clean matrix / vector math (view, projection matrices)
from pyrr import Matrix44, Vector3

# PyOpenGL: Python bindings for the OpenGL C API
from OpenGL.GL import (
    glEnable, glDisable, glClearColor, glClear, glViewport,
    glCreateShader, glShaderSource, glCompileShader,
    glGetShaderiv, glGetShaderInfoLog, glDeleteShader,
    glCreateProgram, glAttachShader, glLinkProgram,
    glGetProgramiv, glGetProgramInfoLog, glUseProgram,
    glGetUniformLocation, glUniformMatrix4fv, glUniform3fv,
    glUniform1f, glUniform1i,
    glGenVertexArrays, glBindVertexArray,
    glGenBuffers, glBindBuffer, glBufferData,
    glEnableVertexAttribArray, glVertexAttribPointer,
    glVertexAttrib3f, glDrawArrays, glLineWidth,
    glDeleteVertexArrays, glDeleteBuffers,
    GL_DEPTH_TEST, GL_MULTISAMPLE, GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT, GL_VERTEX_SHADER, GL_FRAGMENT_SHADER,
    GL_COMPILE_STATUS, GL_LINK_STATUS, GL_ARRAY_BUFFER,
    GL_STATIC_DRAW, GL_STREAM_DRAW, GL_FLOAT, GL_FALSE,
    GL_TRIANGLES, GL_LINE_STRIP, GL_LINES
)


# ──────────────────────────────────────────────────────────
# STEP 1 — SET OPENGL FORMAT (before QApplication is created)
# ──────────────────────────────────────────────────────────
#
# We ask Qt for OpenGL 3.3 Core Profile.
# "Core Profile" means we use ONLY the modern API:
#   - No glBegin/glEnd  (deprecated)
#   - No built-in transforms (deprecated)
#   - Everything goes through VAOs, VBOs, and shaders
#
# We also request:
#   - 4x MSAA for smooth edges
#   - 24-bit depth buffer for correct occlusion
#
def configure_opengl():
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setSamples(4)          # 4× multisampling anti-aliasing
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)


# ──────────────────────────────────────────────────────────
# STEP 2 — GLSL SHADER SOURCE CODE
# ──────────────────────────────────────────────────────────
#
# Shaders are tiny programs that run on the GPU.
# We write two:
#
#   VERTEX SHADER   — runs once per vertex.
#                     Takes 3D position, outputs 2D screen position.
#                     Also passes color/normal to the fragment shader.
#
#   FRAGMENT SHADER — runs once per pixel (fragment).
#                     Calculates the final RGB color with simple lighting.
#
# They're written in GLSL (OpenGL Shading Language), not Python.
# We compile them at runtime inside initializeGL().

VERTEX_SHADER_SRC = """
#version 330 core

// ── Vertex attributes (data from our VBO per vertex) ──
layout(location = 0) in vec3 aPos;      // 3D position in world space
layout(location = 1) in vec3 aNormal;   // surface normal (for lighting)
layout(location = 2) in vec3 aColor;    // per-vertex color

// ── Uniforms (constants set from Python per draw call) ──
uniform mat4 uModel;       // model matrix: local → world space
uniform mat4 uView;        // view matrix:  world → camera space
uniform mat4 uProj;        // projection:   camera → clip space (perspective)
uniform float uSelected;   // 0.0 = normal, 1.0 = selected (adds glow)

// ── Outputs passed to the fragment shader ──
out vec3 vColor;
out vec3 vNormal;
out vec3 vFragPos;   // world-space position (needed for specular lighting)

void main() {
    // Transform position through all three matrices
    vec4 worldPos = uModel * vec4(aPos, 1.0);
    gl_Position   = uProj * uView * worldPos;

    // Pass lighting data to fragment shader
    vFragPos = worldPos.xyz;
    // Transform normals correctly when model is scaled/rotated
    vNormal  = mat3(transpose(inverse(uModel))) * aNormal;

    // Highlight selected objects with a cyan tint
    vec3 selectTint = vec3(0.0, 0.5, 1.0) * uSelected;
    vColor = aColor + selectTint;
}
"""

FRAGMENT_SHADER_SRC = """
#version 330 core

in vec3 vColor;
in vec3 vNormal;
in vec3 vFragPos;

// ── Lighting uniforms ──
uniform vec3  uLightPos;   // world-space position of our single light
uniform vec3  uViewPos;    // camera position (for specular highlight)

out vec4 FragColor;

void main() {
    // ── Ambient ──
    // Ambient light is a flat base brightness so nothing is pitch-black.
    float ambientStrength = 0.3;
    vec3 ambient = ambientStrength * vColor;

    // ── Diffuse ──
    // Diffuse light depends on the angle between the surface normal
    // and the direction toward the light.  max(0) avoids negative light.
    vec3  norm     = normalize(vNormal);
    vec3  lightDir = normalize(uLightPos - vFragPos);
    float diff     = max(dot(norm, lightDir), 0.0);
    vec3  diffuse  = diff * vColor;

    // ── Specular ──
    // Specular is the shiny highlight.  We use Blinn-Phong:
    // compute the halfway vector between light and view directions.
    float specStrength = 0.5;
    vec3  viewDir  = normalize(uViewPos - vFragPos);
    vec3  halfDir  = normalize(lightDir + viewDir);
    float spec     = pow(max(dot(norm, halfDir), 0.0), 64.0);
    vec3  specular = specStrength * spec * vec3(1.0);

    vec3 result = ambient + diffuse + specular;
    FragColor   = vec4(result, 1.0);
}
"""

# A simpler shader for the reference grid (no lighting, just flat color)
GRID_VERT_SRC = """
#version 330 core
layout(location = 0) in vec3 aPos;
uniform mat4 uViewProj;
void main() {
    gl_Position = uViewProj * vec4(aPos, 1.0);
}
"""

GRID_FRAG_SRC = """
#version 330 core
uniform vec3 uColor;
out vec4 FragColor;
void main() {
    FragColor = vec4(uColor, 1.0);
}
"""


# ──────────────────────────────────────────────────────────
# STEP 3 — SHADER COMPILATION HELPER
# ──────────────────────────────────────────────────────────
#
# This function takes GLSL source code, compiles it on the GPU,
# links a vertex+fragment pair into a "program", and returns its ID.
# All subsequent uniform/draw calls reference this integer ID.

def compile_program(vert_src: str, frag_src: str) -> int:
    """Compile and link a GLSL vertex+fragment shader program."""

    def compile_shader(src: str, shader_type) -> int:
        shader = glCreateShader(shader_type)
        glShaderSource(shader, src)
        glCompileShader(shader)
        # Check for compile errors — they show up as a log string
        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(shader).decode()
            raise RuntimeError(f"Shader compile error:\n{log}")
        return shader

    vert = compile_shader(vert_src, GL_VERTEX_SHADER)
    frag = compile_shader(frag_src, GL_FRAGMENT_SHADER)

    prog = glCreateProgram()
    glAttachShader(prog, vert)
    glAttachShader(prog, frag)
    glLinkProgram(prog)
    if not glGetProgramiv(prog, GL_LINK_STATUS):
        log = glGetProgramInfoLog(prog).decode()
        raise RuntimeError(f"Shader link error:\n{log}")

    # Individual shader objects are no longer needed after linking
    glDeleteShader(vert)
    glDeleteShader(frag)
    return prog


# ──────────────────────────────────────────────────────────
# STEP 4 — SPHERE GEOMETRY GENERATOR
# ──────────────────────────────────────────────────────────
#
# We represent each node as a UV sphere.
# A UV sphere is created by looping over latitude and longitude bands
# and building two triangles (a quad) per cell.
#
# Returns: numpy float32 array, shape (N, 9)
#          each row = [x, y, z,  nx, ny, nz,  r, g, b]

def build_sphere(lat_bands: int = 16, lon_bands: int = 16) -> np.ndarray:
    """
    Build a unit sphere (radius=1) centered at origin.
    Returns a flat float32 array ready for glBufferData.
    Layout per vertex: [pos.x, pos.y, pos.z, norm.x, norm.y, norm.z, 1, 1, 1]
    Color is white (1,1,1) — overridden per-draw by uniform or vertex attrib.
    """
    verts = []
    for lat in range(lat_bands):
        # theta goes from -pi/2 (south pole) to +pi/2 (north pole)
        theta0 = np.pi * lat       / lat_bands - np.pi / 2
        theta1 = np.pi * (lat + 1) / lat_bands - np.pi / 2

        for lon in range(lon_bands):
            # phi goes from 0 to 2*pi around the equator
            phi0 = 2 * np.pi * lon       / lon_bands
            phi1 = 2 * np.pi * (lon + 1) / lon_bands

            # Four corners of this quad on the sphere surface
            def point(th, ph):
                x = np.cos(th) * np.cos(ph)
                y = np.sin(th)
                z = np.cos(th) * np.sin(ph)
                # On a unit sphere, the normal equals the position
                return [x, y, z, x, y, z, 1.0, 1.0, 1.0]

            # Split the quad into two triangles (CCW winding)
            p00, p10 = point(theta0, phi0), point(theta1, phi0)
            p01, p11 = point(theta0, phi1), point(theta1, phi1)
            verts += [p00, p10, p11,   # triangle 1
                      p00, p11, p01]   # triangle 2

    return np.array(verts, dtype=np.float32)


# ──────────────────────────────────────────────────────────
# STEP 5 — BEZIER WIRE GEOMETRY
# ──────────────────────────────────────────────────────────
#
# Wires are rendered as cubic Bezier curves.
# A cubic Bezier is defined by 4 control points:
#   P0 (start), P1 (control 1), P2 (control 2), P3 (end)
#
# We automatically generate the two control points so that the wire
# droops downward like a real cable hanging under gravity.
#
# Then we build a tube mesh around the curve using the
# Frenet-Serret frame (tangent, normal, binormal vectors).

def bezier_cubic(p0: np.ndarray, p1: np.ndarray,
                 p2: np.ndarray, p3: np.ndarray,
                 n_segments: int = 24) -> np.ndarray:
    """
    Sample n_segments+1 points along a cubic Bezier curve.
    Returns shape (n_segments+1, 3).

    Formula:  B(t) = (1-t)³·P0 + 3(1-t)²t·P1 + 3(1-t)t²·P2 + t³·P3
    """
    t  = np.linspace(0, 1, n_segments + 1)[:, None]  # column vector
    mt = 1.0 - t
    return (mt**3 * p0
            + 3 * mt**2 * t  * p1
            + 3 * mt    * t**2 * p2
            + t**3            * p3).astype(np.float32)


def wire_control_points(src: np.ndarray, dst: np.ndarray):
    """
    Generate two inner control points for a wire between src and dst.
    The wire droops downward (negative Y) proportional to its length.
    """
    mid  = (src + dst) / 2.0
    span = np.linalg.norm(dst - src)
    sag  = np.array([0.0, -span * 0.30, 0.0], dtype=np.float32)
    return src, mid + sag, mid + sag, dst


def build_tube(spine: np.ndarray, radius: float = 0.06,
               sides: int = 8) -> np.ndarray:
    """
    Build a tube mesh along a spine curve.

    For each point on the spine we compute a local coordinate frame
    (tangent → normal → binormal) and place 'sides' vertices in a ring.
    Adjacent rings are then connected with triangles.

    Returns flat float32 array: [x,y,z, nx,ny,nz, 1,1,1] per vertex.
    """
    rings = []   # list of (sides, 6) arrays — one ring per spine point
    n_pts = len(spine)

    for i in range(n_pts):
        # ── Tangent vector: direction along the spine ──
        if i < n_pts - 1:
            tangent = spine[i + 1] - spine[i]
        else:
            tangent = spine[i] - spine[i - 1]

        norm_t = np.linalg.norm(tangent)
        if norm_t < 1e-8:
            # Degenerate segment — reuse previous frame
            rings.append(rings[-1])
            continue
        tangent /= norm_t

        # ── Build an arbitrary perpendicular vector ──
        # We need any vector not parallel to tangent.
        # Use (0,1,0) unless tangent is nearly vertical.
        ref = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        if abs(np.dot(tangent, ref)) > 0.9:
            ref = np.array([1.0, 0.0, 0.0], dtype=np.float32)

        # Gram-Schmidt: remove the tangent component from ref
        normal   = ref - np.dot(ref, tangent) * tangent
        normal  /= np.linalg.norm(normal)
        binormal = np.cross(tangent, normal)

        # ── Place vertices around the ring ──
        ring_verts = []
        for j in range(sides):
            angle = 2 * np.pi * j / sides
            # Ring vertex = spine point + radius × (cos·normal + sin·binormal)
            outward = np.cos(angle) * normal + np.sin(angle) * binormal
            pos     = spine[i] + radius * outward
            ring_verts.append([*pos, *outward, 1.0, 1.0, 1.0])  # 9 floats

        rings.append(np.array(ring_verts, dtype=np.float32))

    # ── Build triangles between adjacent rings ──
    verts = []
    for i in range(len(rings) - 1):
        for j in range(sides):
            nj = (j + 1) % sides   # wrap around the last vertex
            a, b = rings[i][j],  rings[i][nj]
            c, d = rings[i+1][j], rings[i+1][nj]
            # Two triangles per quad (CCW winding)
            verts += [a, b, d,   a, d, c]

    if not verts:
        return np.zeros((0, 9), dtype=np.float32)

    return np.array(verts, dtype=np.float32)


# ──────────────────────────────────────────────────────────
# STEP 6 — DATA MODEL (pure Python, no OpenGL)
# ──────────────────────────────────────────────────────────
#
# Separating data from rendering is essential for clean code.
# Node/Wire hold all scene state. The renderer reads them.

@dataclass
class Node:
    """
    A node is a sphere in 3D space representing a hardware component
    (RPi, Arduino, sensor, etc.) or a junction point.
    """
    node_id:  int
    position: np.ndarray                         # world-space center
    color:    np.ndarray = field(default_factory=lambda: np.array([0.25, 0.55, 1.0]))
    radius:   float      = 0.4
    label:    str        = "Node"
    selected: bool       = False

    def __post_init__(self):
        self.position = np.array(self.position, dtype=np.float32)
        self.color    = np.array(self.color,    dtype=np.float32)


@dataclass
class Wire:
    """
    A wire connects exactly two nodes with a Bezier tube.
    """
    wire_id: int
    src_id:  int          # source node ID
    dst_id:  int          # destination node ID
    color:   np.ndarray = field(default_factory=lambda: np.array([1.0, 0.65, 0.1]))
    thickness: float    = 0.06
    selected:  bool     = False

    def __post_init__(self):
        self.color = np.array(self.color, dtype=np.float32)


class SceneGraph:
    """
    Holds all nodes and wires.  The renderer reads this every frame.
    Setting 'dirty = True' signals the renderer to rebuild GPU buffers.
    """
    def __init__(self):
        self.nodes: Dict[int, Node] = {}
        self.wires: Dict[int, Wire] = {}
        self._next_node_id = 0
        self._next_wire_id = 0
        self.dirty = True  # GPU buffers need rebuild

    def add_node(self, position, color=None, label="Node") -> Node:
        nid = self._next_node_id
        self._next_node_id += 1
        color = color or [
            random.uniform(0.2, 1.0),
            random.uniform(0.2, 1.0),
            random.uniform(0.2, 1.0)
        ]
        n = Node(node_id=nid, position=np.array(position, np.float32),
                 color=np.array(color, np.float32), label=label)
        self.nodes[nid] = n
        self.dirty = True
        return n

    def remove_node(self, node_id: int):
        if node_id not in self.nodes:
            return
        del self.nodes[node_id]
        # Remove all wires attached to this node
        to_remove = [wid for wid, w in self.wires.items()
                     if w.src_id == node_id or w.dst_id == node_id]
        for wid in to_remove:
            del self.wires[wid]
        self.dirty = True

    def add_wire(self, src_id: int, dst_id: int, color=None) -> Optional[Wire]:
        if src_id not in self.nodes or dst_id not in self.nodes:
            return None
        if src_id == dst_id:
            return None
        # Prevent duplicate wires
        for w in self.wires.values():
            if {w.src_id, w.dst_id} == {src_id, dst_id}:
                return None
        wid = self._next_wire_id
        self._next_wire_id += 1
        color = color or [
            random.uniform(0.6, 1.0),
            random.uniform(0.3, 0.8),
            random.uniform(0.1, 0.4)
        ]
        w = Wire(wire_id=wid, src_id=src_id, dst_id=dst_id,
                 color=np.array(color, np.float32))
        self.wires[wid] = w
        self.dirty = True
        return w

    def deselect_all(self):
        for n in self.nodes.values():
            n.selected = False
        for w in self.wires.values():
            w.selected = False


# ──────────────────────────────────────────────────────────
# STEP 7 — ORBIT CAMERA
# ──────────────────────────────────────────────────────────
#
# The camera orbits around a 'target' point.
# We store (yaw, pitch, distance) in spherical coordinates.
# From those we derive the camera position, then build
# view and projection matrices for the shader.

class OrbitCamera:
    """
    Spherical orbit camera.
    - Yaw:      horizontal rotation around Y axis (degrees)
    - Pitch:    vertical tilt (degrees, clamped to ±89 to avoid gimbal lock)
    - Distance: how far the camera is from the target
    - Target:   the world-space point being looked at
    """
    def __init__(self):
        self.yaw      = -35.0
        self.pitch    =  30.0
        self.distance =  14.0
        self.target   = np.zeros(3, dtype=np.float32)
        self.aspect   = 1.0
        self._last_pos = None
        self._mode     = None   # 'orbit' | 'pan'

    @property
    def position(self) -> np.ndarray:
        """Compute eye position in world space from spherical coords."""
        yr = np.radians(self.yaw)
        pr = np.radians(self.pitch)
        return self.target + self.distance * np.array([
            np.cos(pr) * np.sin(yr),
            np.sin(pr),
            np.cos(pr) * np.cos(yr)
        ], dtype=np.float32)

    def view_matrix(self) -> np.ndarray:
        """
        The view matrix transforms world coordinates into camera space.
        It is the inverse of the camera's model matrix.
        pyrr's look_at() handles this for us.
        """
        return Matrix44.look_at(
            self.position,
            self.target,
            Vector3([0.0, 1.0, 0.0]),
            dtype=np.float32
        )

    def proj_matrix(self) -> np.ndarray:
        """
        Perspective projection matrix.
        fov=45°, near=0.05, far=500.
        Objects outside [near, far] are clipped.
        """
        return Matrix44.perspective_projection(
            45.0, self.aspect, 0.05, 500.0,
            dtype=np.float32
        )

    def set_aspect(self, w: int, h: int):
        self.aspect = w / max(h, 1)

    # ── Mouse handlers — called from Qt events ──

    def mouse_press(self, x: float, y: float, button):
        self._last_pos = (x, y)
        if button == Qt.MouseButton.LeftButton:
            self._mode = 'orbit'
        elif button == Qt.MouseButton.MiddleButton:
            self._mode = 'pan'

    def mouse_move(self, x: float, y: float):
        if self._last_pos is None or self._mode is None:
            return
        dx = x - self._last_pos[0]
        dy = y - self._last_pos[1]
        self._last_pos = (x, y)

        if self._mode == 'orbit':
            # Drag rotates the camera around the target
            self.yaw   += dx * 0.45
            self.pitch += dy * 0.45
            self.pitch  = float(np.clip(self.pitch, -88.0, 88.0))

        elif self._mode == 'pan':
            # Drag moves the target in the camera's local XY plane
            # We need the camera's right and up vectors for this
            fwd   = self.target - self.position
            right = np.cross(fwd, [0, 1, 0])
            if np.linalg.norm(right) < 1e-6:
                right = np.array([1, 0, 0], dtype=np.float32)
            right /= np.linalg.norm(right)
            up = np.array([0, 1, 0], dtype=np.float32)
            speed = self.distance * 0.0025
            self.target -= (right * dx + up * (-dy)) * speed

    def mouse_release(self):
        self._mode = None

    def scroll(self, delta: float):
        """Positive delta = zoom in (smaller distance)."""
        factor = 0.88 if delta > 0 else 1.14
        self.distance = float(np.clip(self.distance * factor, 0.5, 300.0))

    def reset(self):
        self.yaw, self.pitch, self.distance = -35.0, 30.0, 14.0
        self.target = np.zeros(3, dtype=np.float32)


# ──────────────────────────────────────────────────────────
# STEP 8 — MOUSE PICKING (RAY CASTING)
# ──────────────────────────────────────────────────────────
#
# When the user clicks in the 3D viewport, we need to know
# which node (if any) they clicked.
#
# Process:
#   1. Convert 2D mouse position to Normalized Device Coordinates (NDC)
#   2. Unproject through the inverse projection matrix → eye-space ray
#   3. Unproject through the inverse view matrix → world-space ray
#   4. Test the ray against each node's bounding sphere
#   5. Return the closest hit

def screen_to_ray(mouse_x: float, mouse_y: float,
                  width: int, height: int,
                  proj: np.ndarray,
                  view: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert 2D screen click to a 3D world-space ray.

    Returns:
        origin    — ray start (camera position)
        direction — normalized ray direction (unit vector)
    """
    # Step 1: Screen pixels → NDC ([-1, +1] in both axes)
    # NDC x: left=−1, right=+1
    # NDC y: top=+1, bottom=−1 (note the flip — screen Y is inverted)
    ndc_x = (2.0 * mouse_x) / width  - 1.0
    ndc_y = 1.0 - (2.0 * mouse_y) / height

    # Step 2: NDC → eye space
    # We use the inverse projection matrix.
    # The ray points into the screen (z = -1.0 in OpenGL convention).
    inv_proj = np.linalg.inv(proj)
    clip_coords = np.array([ndc_x, ndc_y, -1.0, 1.0], dtype=np.float64)
    eye_coords  = inv_proj @ clip_coords
    # We only care about direction; force z=-1, w=0 (vector, not point)
    eye_ray = np.array([eye_coords[0], eye_coords[1], -1.0, 0.0])

    # Step 3: Eye space → world space
    inv_view  = np.linalg.inv(view)
    world_ray = inv_view @ eye_ray
    direction = world_ray[:3]

    norm = np.linalg.norm(direction)
    if norm > 1e-8:
        direction /= norm

    # The ray originates from the camera position
    origin = inv_view @ np.array([0, 0, 0, 1], dtype=np.float64)
    return origin[:3].astype(np.float32), direction.astype(np.float32)


def ray_sphere_hit(ray_origin: np.ndarray, ray_dir: np.ndarray,
                   center: np.ndarray, radius: float) -> float:
    """
    Analytic ray-sphere intersection.

    Solves: |O + t·D - C|² = r²
    Rearranged into quadratic: at² + bt + c = 0

    Returns t (distance along ray to nearest hit), or -1 if no hit.
    """
    oc   = ray_origin - center
    a    = np.dot(ray_dir, ray_dir)
    b    = 2.0 * np.dot(oc, ray_dir)
    c    = np.dot(oc, oc) - radius * radius
    disc = b * b - 4 * a * c

    if disc < 0:
        return -1.0   # ray misses the sphere entirely

    return (-b - np.sqrt(disc)) / (2.0 * a)


def pick_node(scene: SceneGraph, ray_origin, ray_dir) -> Optional[int]:
    """
    Find the node (if any) that the ray hits.
    Returns the node_id of the closest hit, or None.
    """
    best_t = float('inf')
    best_id = None

    for node in scene.nodes.values():
        # Use a slightly larger pick radius so small nodes are easy to click
        t = ray_sphere_hit(ray_origin, ray_dir, node.position, node.radius * 1.3)
        if 0.0 < t < best_t:
            best_t  = t
            best_id = node.node_id

    return best_id


# ──────────────────────────────────────────────────────────
# STEP 9 — GPU BUFFER HELPERS
# ──────────────────────────────────────────────────────────
#
# A VAO (Vertex Array Object) remembers:
#   - which VBO to read from
#   - how many bytes per vertex (stride)
#   - where each attribute is in that stride
#
# A VBO (Vertex Buffer Object) is a block of raw float data on the GPU.

def create_vao_vbo(data: np.ndarray) -> tuple[int, int]:
    """
    Upload a numpy float32 array to the GPU.

    Expects columns: [x,y,z, nx,ny,nz, r,g,b]  (9 floats per vertex)

    Returns (vao_id, vbo_id) — the VAO remembers the layout.
    """
    if len(data) == 0:
        return 0, 0

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    stride = 9 * 4  # 9 floats × 4 bytes each = 36 bytes per vertex

    # Attribute 0: position  (floats 0-2)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)

    # Attribute 1: normal    (floats 3-5)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride,
                          ctypes.c_void_p(3 * 4))

    # Attribute 2: color     (floats 6-8)
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride,
                          ctypes.c_void_p(6 * 4))

    glBindVertexArray(0)
    return vao, vbo


def delete_vao_vbo(vao: int, vbo: int):
    """Free GPU memory for a VAO+VBO pair."""
    if vao:
        glDeleteVertexArrays(1, [vao])
    if vbo:
        glDeleteBuffers(1, [vbo])


# ──────────────────────────────────────────────────────────
# STEP 10 — REFERENCE GRID
# ──────────────────────────────────────────────────────────
#
# A simple flat grid drawn with GL_LINES helps users understand
# the 3D space orientation.

def build_grid(half_size: int = 10, step: int = 1) -> np.ndarray:
    """
    Build a flat XZ grid of lines.
    Returns float32 array of line endpoint pairs: [x, y, z] per point.
    """
    verts = []
    for i in range(-half_size, half_size + 1, step):
        # Lines parallel to Z axis
        verts += [[i, 0, -half_size], [i, 0,  half_size]]
        # Lines parallel to X axis
        verts += [[-half_size, 0, i], [ half_size, 0, i]]
    return np.array(verts, dtype=np.float32)


# ──────────────────────────────────────────────────────────
# STEP 11 — THE MAIN OPENGL WIDGET
# ──────────────────────────────────────────────────────────
#
# QOpenGLWidget gives us an OpenGL context embedded in a Qt window.
# We override three methods:
#   initializeGL() — called once when context is ready
#   resizeGL()     — called on window resize
#   paintGL()      — called every time the widget needs to redraw

class WireGraphWidget(QOpenGLWidget):

    def __init__(self, scene: SceneGraph, camera: OrbitCamera, parent=None):
        super().__init__(parent)
        self.scene  = scene
        self.camera = camera

        # GPU resource handles (set in initializeGL)
        self.prog      = 0    # shader program for nodes/wires
        self.grid_prog = 0    # shader program for the grid

        # Pre-built sphere geometry (shared by all nodes)
        self._sphere_vao = 0
        self._sphere_vbo = 0
        self._sphere_vert_count = 0

        # Grid geometry
        self._grid_vao = 0
        self._grid_vbo = 0
        self._grid_count = 0

        # Per-wire GPU buffers: wire_id → (vao, vbo, vert_count)
        self._wire_buffers: Dict[int, tuple] = {}

        # Track which nodes' wire buffers need rebuilding
        self._last_node_positions: Dict[int, np.ndarray] = {}

        # Selected node tracking
        self._selection_callback = None  # called with node_id or None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(600, 400)

    # ──────────────────────────────────────────────────────
    # initializeGL — runs once, here we compile shaders and
    # upload static geometry
    # ──────────────────────────────────────────────────────
    def initializeGL(self):
        # Global GL state
        glEnable(GL_DEPTH_TEST)   # correct occlusion (front hides back)
        glEnable(GL_MULTISAMPLE)  # smooth edges (requires fmt.setSamples)
        glClearColor(0.06, 0.09, 0.13, 1.0)  # dark navy background

        # Compile shader programs
        self.prog      = compile_program(VERTEX_SHADER_SRC, FRAGMENT_SHADER_SRC)
        self.grid_prog = compile_program(GRID_VERT_SRC, GRID_FRAG_SRC)

        # Build and upload the shared sphere mesh
        sphere_data = build_sphere(lat_bands=18, lon_bands=18)
        self._sphere_vao, self._sphere_vbo = create_vao_vbo(sphere_data)
        # Each row in sphere_data is one vertex; triangles = verts / 3
        self._sphere_vert_count = len(sphere_data)

        # Build and upload the reference grid (uses a simpler shader)
        grid_data = build_grid(half_size=12, step=1)
        self._grid_vao = glGenVertexArrays(1)
        self._grid_vbo = glGenBuffers(1)
        glBindVertexArray(self._grid_vao)
        glBindBuffer(GL_ARRAY_BUFFER, self._grid_vbo)
        glBufferData(GL_ARRAY_BUFFER, grid_data.nbytes, grid_data, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindVertexArray(0)
        self._grid_count = len(grid_data)

        # Force rebuild of wire buffers on first paint
        self.scene.dirty = True

    # ──────────────────────────────────────────────────────
    # resizeGL — adjust the viewport and camera aspect ratio
    # ──────────────────────────────────────────────────────
    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        self.camera.set_aspect(w, h)

    # ──────────────────────────────────────────────────────
    # paintGL — the main render loop, called every frame
    # ──────────────────────────────────────────────────────
    def paintGL(self):
        # Clear color and depth buffers before drawing anything
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # If nodes/wires changed, rebuild wire GPU buffers
        if self.scene.dirty:
            self._rebuild_wire_buffers()
            self.scene.dirty = False

        # Compute matrices that are shared by all objects this frame
        view = self.camera.view_matrix()
        proj = self.camera.proj_matrix()
        vp   = proj @ view   # combined view-projection (for grid)

        # ── Draw reference grid ──
        self._draw_grid(vp)

        # ── Draw wires (behind nodes) ──
        self._draw_wires(view, proj)

        # ── Draw nodes (spheres on top) ──
        self._draw_nodes(view, proj)

    # ──────────────────────────────────────────────────────
    # _rebuild_wire_buffers
    # Called when scene.dirty is True — regenerates tube geometry
    # for every wire and uploads it to the GPU.
    # ──────────────────────────────────────────────────────
    def _rebuild_wire_buffers(self):
        # Delete buffers for wires that no longer exist
        existing_wids = set(self.scene.wires.keys())
        for wid in list(self._wire_buffers.keys()):
            if wid not in existing_wids:
                vao, vbo, _ = self._wire_buffers.pop(wid)
                delete_vao_vbo(vao, vbo)

        # Create/update buffers for every wire
        for wid, wire in self.scene.wires.items():
            src = self.scene.nodes.get(wire.src_id)
            dst = self.scene.nodes.get(wire.dst_id)
            if src is None or dst is None:
                continue

            # Generate the Bezier spine, then the tube mesh around it
            p0, p1, p2, p3 = wire_control_points(src.position, dst.position)
            spine    = bezier_cubic(p0, p1, p2, p3, n_segments=28)
            tube     = build_tube(spine, radius=wire.thickness, sides=8)

            # Color the entire tube with the wire's color
            if len(tube) > 0:
                tube[:, 6:9] = wire.color  # columns 6-8 are RGB

            # Delete old buffer if this wire already had one
            if wid in self._wire_buffers:
                old_vao, old_vbo, _ = self._wire_buffers[wid]
                delete_vao_vbo(old_vao, old_vbo)

            if len(tube) > 0:
                vao, vbo = create_vao_vbo(tube)
                self._wire_buffers[wid] = (vao, vbo, len(tube))
            else:
                self._wire_buffers[wid] = (0, 0, 0)

    # ──────────────────────────────────────────────────────
    # _draw_grid
    # ──────────────────────────────────────────────────────
    def _draw_grid(self, viewproj: np.ndarray):
        glUseProgram(self.grid_prog)
        loc_vp    = glGetUniformLocation(self.grid_prog, 'uViewProj')
        loc_color = glGetUniformLocation(self.grid_prog, 'uColor')
        glUniformMatrix4fv(loc_vp, 1, GL_FALSE, viewproj)
        glUniform3fv(loc_color, 1, np.array([0.12, 0.20, 0.28], np.float32))

        glLineWidth(1.0)
        glBindVertexArray(self._grid_vao)
        glDrawArrays(GL_LINES, 0, self._grid_count)
        glBindVertexArray(0)

    # ──────────────────────────────────────────────────────
    # _draw_nodes
    # Each node is the same sphere mesh but placed in world space
    # by its own model matrix (translate × scale).
    # ──────────────────────────────────────────────────────
    def _draw_nodes(self, view: np.ndarray, proj: np.ndarray):
        glUseProgram(self.prog)

        # Cache uniform locations (getting them every frame is fine for small scenes)
        loc_model    = glGetUniformLocation(self.prog, 'uModel')
        loc_view     = glGetUniformLocation(self.prog, 'uView')
        loc_proj     = glGetUniformLocation(self.prog, 'uProj')
        loc_selected = glGetUniformLocation(self.prog, 'uSelected')
        loc_light    = glGetUniformLocation(self.prog, 'uLightPos')
        loc_viewpos  = glGetUniformLocation(self.prog, 'uViewPos')

        # Upload shared uniforms (same for all nodes this frame)
        glUniformMatrix4fv(loc_view, 1, GL_FALSE, view)
        glUniformMatrix4fv(loc_proj, 1, GL_FALSE, proj)
        glUniform3fv(loc_light,   1, np.array([8.0, 12.0, 8.0], np.float32))
        glUniform3fv(loc_viewpos, 1, self.camera.position)

        glBindVertexArray(self._sphere_vao)

        for node in self.scene.values() if hasattr(self.scene, 'values') \
                else self.scene.nodes.values():

            # Build a model matrix: scale the unit sphere, then translate it
            # Matrix44.from_translation and from_scale return 4×4 matrices
            scale_m = Matrix44.from_scale(
                [node.radius, node.radius, node.radius], dtype=np.float32)
            trans_m = Matrix44.from_translation(node.position, dtype=np.float32)
            model   = trans_m @ scale_m  # translate AFTER scale

            glUniformMatrix4fv(loc_model, 1, GL_FALSE, model)
            glUniform1f(loc_selected, 1.0 if node.selected else 0.0)

            # Inject the node color into attribute slot 2 as a constant
            # (glVertexAttrib3f sets a constant value — not from VBO)
            glVertexAttrib3f(2, *node.color)

            glDrawArrays(GL_TRIANGLES, 0, self._sphere_vert_count)

        glBindVertexArray(0)

    # ──────────────────────────────────────────────────────
    # _draw_wires
    # Each wire has its own VAO/VBO with pre-built tube geometry.
    # The model matrix is identity (positions are baked into the tube).
    # ──────────────────────────────────────────────────────
    def _draw_wires(self, view: np.ndarray, proj: np.ndarray):
        glUseProgram(self.prog)

        loc_model    = glGetUniformLocation(self.prog, 'uModel')
        loc_view     = glGetUniformLocation(self.prog, 'uView')
        loc_proj     = glGetUniformLocation(self.prog, 'uProj')
        loc_selected = glGetUniformLocation(self.prog, 'uSelected')
        loc_light    = glGetUniformLocation(self.prog, 'uLightPos')
        loc_viewpos  = glGetUniformLocation(self.prog, 'uViewPos')

        # Identity model matrix — wire vertices are in world space already
        identity = Matrix44.identity(dtype=np.float32)

        glUniformMatrix4fv(loc_model,   1, GL_FALSE, identity)
        glUniformMatrix4fv(loc_view,    1, GL_FALSE, view)
        glUniformMatrix4fv(loc_proj,    1, GL_FALSE, proj)
        glUniform3fv(loc_light,         1, np.array([8.0, 12.0, 8.0], np.float32))
        glUniform3fv(loc_viewpos,       1, self.camera.position)

        for wid, wire in self.scene.wires.items():
            buf = self._wire_buffers.get(wid)
            if buf is None:
                continue
            vao, vbo, count = buf
            if vao == 0 or count == 0:
                continue

            glUniform1f(loc_selected, 1.0 if wire.selected else 0.0)
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, count)

        glBindVertexArray(0)

    # ──────────────────────────────────────────────────────
    # Mouse / Keyboard event handlers
    # ──────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        pos = event.position()
        x, y = pos.x(), pos.y()

        if event.button() == Qt.MouseButton.LeftButton:
            # Try to pick a node first
            view = self.camera.view_matrix()
            proj = self.camera.proj_matrix()
            ray_origin, ray_dir = screen_to_ray(
                x, y, self.width(), self.height(),
                proj, view
            )
            picked_id = pick_node(self.scene, ray_origin, ray_dir)

            # Deselect all, then select the hit node
            self.scene.deselect_all()
            if picked_id is not None:
                self.scene.nodes[picked_id].selected = True

            if self._selection_callback:
                self._selection_callback(picked_id)

            self.scene.dirty = True
            self.update()

        # Start camera drag (orbit on Left if not picking, pan on Middle)
        self.camera.mouse_press(x, y, event.button())

    def mouseMoveEvent(self, event):
        pos = event.position()
        # Only move camera when a button is held
        if event.buttons() != Qt.MouseButton.NoButton:
            self.camera.mouse_move(pos.x(), pos.y())
            self.update()

    def mouseReleaseEvent(self, event):
        self.camera.mouse_release()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera.scroll(delta / 120.0)
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_R:
            self.camera.reset()
            self.update()
        elif key == Qt.Key.Key_Escape:
            QApplication.quit()
        # Other keys are handled by the main window
        else:
            event.ignore()

    def set_selection_callback(self, cb):
        """Register a function called with selected node_id (or None)."""
        self._selection_callback = cb


# ──────────────────────────────────────────────────────────
# STEP 12 — MAIN WINDOW (Qt UI wrapper)
# ──────────────────────────────────────────────────────────
#
# The main window contains:
#   - The 3D viewport (WireGraphWidget) — takes most of the space
#   - A right-side panel with info and buttons
#   - Status bar showing selected node

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Wiring System — PyQt6 + OpenGL")
        self.resize(1200, 750)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #0d1520; color: #b8ccd9; }
            QLabel { color: #b8ccd9; }
            QPushButton {
                background: #1a2d40; color: #00d4ff;
                border: 1px solid #1e3550; border-radius: 3px;
                padding: 6px 14px; font-size: 12px;
            }
            QPushButton:hover  { background: #1e3550; border-color: #00d4ff; }
            QPushButton:pressed { background: #0d2030; }
            QFrame { border: 1px solid #1e3550; border-radius: 4px; }
        """)

        # Scene and camera — shared between widget and window
        self.scene  = SceneGraph()
        self.camera = OrbitCamera()

        # Track last two selected node IDs for wire creation
        self._last_selected: List[int] = []

        # Populate with a demo scene
        self._build_demo_scene()

        # ── Layout ──
        central = QWidget()
        self.setCentralWidget(central)
        hbox = QHBoxLayout(central)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        # 3D Viewport
        self.gl_widget = WireGraphWidget(self.scene, self.camera)
        self.gl_widget.set_selection_callback(self._on_node_selected)
        hbox.addWidget(self.gl_widget, stretch=1)

        # Side panel
        panel = self._build_panel()
        hbox.addWidget(panel)

        # Status bar at the bottom
        self.statusBar().setStyleSheet(
            "background: #080f16; color: #3a5567; font-size: 11px; padding: 2px 8px;")
        self.statusBar().showMessage(
            "Left-drag: orbit  |  Middle-drag: pan  |  Scroll: zoom  |  Click: select  |  A: add node  |  W: connect  |  Del: remove  |  R: reset")

    # ──────────────────────────────────────────────────────
    # Demo scene — shows off the system on startup
    # ──────────────────────────────────────────────────────
    def _build_demo_scene(self):
        # Add several nodes representing different hardware
        rpi   = self.scene.add_node([ 0.0, 0.0,  0.0], color=[0.2, 0.6, 1.0],  label="Raspberry Pi 4")
        ard   = self.scene.add_node([ 4.5, 0.0,  2.0], color=[0.2, 0.85, 0.35], label="Arduino Uno")
        sen1  = self.scene.add_node([-3.5, 0.0,  2.5], color=[1.0, 0.6, 0.15],  label="Temp Sensor")
        sen2  = self.scene.add_node([ 2.0, 0.0, -4.0], color=[0.9, 0.3, 0.3],   label="Motor Driver")
        hub   = self.scene.add_node([-1.5, 0.0, -3.0], color=[0.75, 0.4, 1.0],  label="USB Hub")
        pwr   = self.scene.add_node([ 5.5, 0.0, -2.0], color=[1.0, 0.85, 0.1],  label="Power Supply")
        led   = self.scene.add_node([-5.0, 0.0, -1.5], color=[0.95, 0.95, 0.95],label="LED Strip")

        # Wire them up with different colors
        self.scene.add_wire(rpi.node_id,  ard.node_id,  color=[0.95, 0.55, 0.05])  # orange
        self.scene.add_wire(rpi.node_id,  sen1.node_id, color=[0.2,  0.9,  0.4])   # green
        self.scene.add_wire(rpi.node_id,  sen2.node_id, color=[0.9,  0.2,  0.25])  # red
        self.scene.add_wire(rpi.node_id,  hub.node_id,  color=[0.4,  0.7,  1.0])   # blue
        self.scene.add_wire(ard.node_id,  pwr.node_id,  color=[1.0,  0.9,  0.1])   # yellow
        self.scene.add_wire(ard.node_id,  sen2.node_id, color=[0.9,  0.5,  0.1])   # amber
        self.scene.add_wire(hub.node_id,  led.node_id,  color=[0.85, 0.25, 1.0])   # purple
        self.scene.add_wire(pwr.node_id,  sen2.node_id, color=[1.0,  0.4,  0.4])   # red-orange

    # ──────────────────────────────────────────────────────
    # Side panel
    # ──────────────────────────────────────────────────────
    def _build_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(220)
        panel.setStyleSheet("background: #080f16; border-left: 1px solid #1a2a3a;")
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(14, 18, 14, 14)
        vbox.setSpacing(10)

        # Title
        title = QLabel("3D WIRE SYSTEM")
        title.setFont(QFont("monospace", 10))
        title.setStyleSheet("color: #00d4ff; letter-spacing: 2px; font-weight: bold;")
        vbox.addWidget(title)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("border: 1px solid #1a2a3a;")
        vbox.addWidget(sep)

        # Selection info
        self.sel_label = QLabel("Nothing selected")
        self.sel_label.setStyleSheet("color: #3a5567; font-size: 11px;")
        self.sel_label.setWordWrap(True)
        vbox.addWidget(self.sel_label)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #00ff88; font-size: 11px;")
        self.info_label.setWordWrap(True)
        vbox.addWidget(self.info_label)

        vbox.addSpacing(8)

        # Buttons
        def btn(text, handler):
            b = QPushButton(text)
            b.clicked.connect(handler)
            vbox.addWidget(b)
            return b

        btn("➕  Add Node  [A]",      self._add_random_node)
        btn("🔗  Connect Last 2  [W]", self._connect_selected)
        btn("🗑  Delete Selected [Del]",self._delete_selected)
        btn("↺  Reset Camera  [R]",   self._reset_camera)
        btn("🔄  Clear All",           self._clear_all)

        vbox.addSpacing(8)
        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("border: 1px solid #1a2a3a;")
        vbox.addWidget(sep2)

        # Stats
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #3a5567; font-size: 11px; line-height: 1.5;")
        self.stats_label.setWordWrap(True)
        vbox.addWidget(self.stats_label)
        self._update_stats()

        vbox.addStretch()

        # Help
        help_text = QLabel(
            "Controls:\n"
            "  Left-drag  → orbit\n"
            "  Mid-drag   → pan\n"
            "  Scroll     → zoom\n"
            "  Click      → select\n"
            "  A          → add node\n"
            "  W          → connect 2\n"
            "  Del        → remove\n"
            "  R          → reset cam"
        )
        help_text.setStyleSheet("color: #2a3f52; font-size: 10px;")
        vbox.addWidget(help_text)

        return panel

    # ──────────────────────────────────────────────────────
    # Actions
    # ──────────────────────────────────────────────────────

    def _add_random_node(self):
        x = random.uniform(-6, 6)
        z = random.uniform(-6, 6)
        labels = ["Sensor", "MCU", "Gateway", "Driver", "Relay", "Display", "Module"]
        self.scene.add_node([x, 0, z], label=random.choice(labels))
        self._update_stats()
        self.gl_widget.update()

    def _connect_selected(self):
        """Connect the last two selected nodes with a wire."""
        if len(self._last_selected) >= 2:
            a, b = self._last_selected[-2], self._last_selected[-1]
            w = self.scene.add_wire(a, b)
            if w:
                self.info_label.setText(f"Wire added\n{a} → {b}")
            else:
                self.info_label.setText("Already connected\nor same node!")
            self._update_stats()
            self.gl_widget.update()

    def _delete_selected(self):
        sel = [n.node_id for n in self.scene.nodes.values() if n.selected]
        for nid in sel:
            if nid in self._last_selected:
                self._last_selected.remove(nid)
            self.scene.remove_node(nid)
        self.sel_label.setText("Nothing selected")
        self.info_label.setText(f"Removed {len(sel)} node(s)")
        self._update_stats()
        self.gl_widget.update()

    def _reset_camera(self):
        self.camera.reset()
        self.gl_widget.update()

    def _clear_all(self):
        self.scene.nodes.clear()
        self.scene.wires.clear()
        self.scene.dirty = True
        self._last_selected.clear()
        self.sel_label.setText("Nothing selected")
        self.info_label.setText("Scene cleared")
        self._update_stats()
        self.gl_widget.update()

    def _on_node_selected(self, node_id: Optional[int]):
        if node_id is not None:
            node = self.scene.nodes.get(node_id)
            if node:
                self.sel_label.setText(f"Selected:\n{node.label}\nID: {node_id}")
                pos = node.position
                self.info_label.setText(
                    f"Pos: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
                # Track for wire connection
                if node_id not in self._last_selected:
                    self._last_selected.append(node_id)
                if len(self._last_selected) > 2:
                    self._last_selected = self._last_selected[-2:]
        else:
            self.sel_label.setText("Nothing selected")
            self.info_label.setText("")

    def _update_stats(self):
        n = len(self.scene.nodes)
        w = len(self.scene.wires)
        self.stats_label.setText(f"Nodes : {n}\nWires : {w}")

    # ──────────────────────────────────────────────────────
    # Key events (window-level, catches A/W/Delete)
    # ──────────────────────────────────────────────────────
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key.Key_A:
            self._add_random_node()
        elif key == Qt.Key.Key_W:
            self._connect_selected()
        elif key in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            self._delete_selected()
        elif key == Qt.Key.Key_R:
            self._reset_camera()
        elif key == Qt.Key.Key_Escape:
            QApplication.quit()
        else:
            super().keyPressEvent(event)


# ──────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────

def main():
    # IMPORTANT: configure the OpenGL format BEFORE creating QApplication.
    # Once QApplication is created, the format is locked in.
    configure_opengl()

    app = QApplication(sys.argv)
    app.setApplicationName("3D Wiring System")

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
