"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
// Variable Declarations
let socket = null;
let commandSent = false;
let dragOffset = { x: 0, y: 0 };
let ghostElements = [];
let currentDraggedElement = null;
let targetElement = null;
let ghostUpdateTimeout = null;
let originalPositions = new Map();
let lastHoveredElement = null;
let activeDraggable = null;
let draggables = [];
let thresholdIndicator = null;
let nocolseelements = false;
let positionIndicator = null;
// Update the executeCommand function
function executeCommand(element) {
    return __awaiter(this, void 0, void 0, function* () {
        return new Promise((resolve) => {
            let isStop = false;
            let isDraggable1 = false;
            let isWait = false;
            if (element.id.startsWith("draggable1-")) {
                isDraggable1 = true;
            }
            if (element.id.startsWith("draggable3-")) {
                isStop = true;
            }
            if (element.id.startsWith("draggable4-")) {
                isWait = true;
            }
            console.log("Executing command for:", element.id, "isStop:", isStop);
            if (isStop) {
                handleStop(element);
                setTimeout(resolve, 1);
            }
            else if (isDraggable1) {
                handleDraggable1Send(element);
                setTimeout(resolve, 1);
            }
            else if (isWait) {
                handleWait(element);
                setTimeout(resolve, 1);
            }
        });
    });
}
function handleWait(element) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open");
        initializeWebSocket();
        return;
    }
    const durationInput = element.querySelector(".duration-input");
    try {
        const duration = parseInt((durationInput === null || durationInput === void 0 ? void 0 : durationInput.value) || "1");
        const direction = 0;
        const speed = 0;
        const message = `stop  ${direction} ${speed} ${duration}`;
        console.log("Sending message:", message);
        socket.send(message);
    }
    catch (error) {
        console.error("Error sending message:", error);
    }
    console.log("Sent command for:", element.id);
}
function handleStop(element) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open");
        initializeWebSocket();
        return;
    }
    console.log("Found STOP element, sending stop command...");
    try {
        const direction = 0;
        const speed = 0;
        const duration = 0;
        const message = `stop ${direction} ${speed} ${duration}`;
        console.log("Sending message:", message);
        if (socket) {
            socket.send(message);
        }
    }
    catch (error) {
        console.error("Error sending stop message:", error);
    }
}
function handleDraggable1Send(element) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error("WebSocket is not open");
        initializeWebSocket();
        return;
    }
    const durationInput = element.querySelector(".duration-input");
    const directionSelect = element.querySelector(".direction-select");
    const input = element.querySelector(".number-input");
    if (!directionSelect || !input) {
        console.error("Required elements not found in", element);
        return;
    }
    try {
        const duration = parseInt((durationInput === null || durationInput === void 0 ? void 0 : durationInput.value) || "1");
        const direction = (directionSelect === null || directionSelect === void 0 ? void 0 : directionSelect.value) || 1;
        const speed = Math.min(Math.max(parseInt(input.value || "0"), 0), 100);
        const message = `start ${direction} ${speed} ${duration}`;
        console.log("Sending message:", message);
        socket.send(message);
    }
    catch (error) {
        console.error("Error sending message:", error);
    }
    console.log("Sent command for:", element.id);
}
document.addEventListener("DOMContentLoaded", () => {
    const commandButton = document.getElementById("command-button");
    if (commandButton) {
        commandButton.addEventListener("click", (event) => __awaiter(void 0, void 0, void 0, function* () {
            // Prevent event bubbling
            event.stopPropagation();
            console.log("Command button clicked, starting scan...");
            // Find START elements
            const startElements = draggables.filter((id) => id.startsWith("draggable2-"));
            console.log("Found START elements:", startElements.length);
            for (const startElementId of startElements) {
                const startElement = document.getElementById(startElementId);
                if (!startElement)
                    continue;
                const startRect = startElement.getBoundingClientRect();
                // Find elements below START
                const belowElements = draggables
                    .filter((id) => id.startsWith("draggable1-") ||
                    id.startsWith("draggable3-") ||
                    id.startsWith("draggable4-"))
                    .map((id) => document.getElementById(id))
                    .filter((element) => element !== null)
                    .filter((element) => {
                    let isDraggable1 = false;
                    let isStop = false;
                    let isWait = false;
                    if (element.id.startsWith("draggable1-")) {
                        isDraggable1 = true;
                    }
                    if (element.id.startsWith("draggable3-")) {
                        isStop = true;
                    }
                    if (element.id.startsWith("draggable4-")) {
                        isWait = true;
                    }
                    const rect = element.getBoundingClientRect();
                    const isBelow = rect.top > startRect.bottom;
                    console.log("Checking element:", {
                        id: element.id,
                        isDraggable1,
                        isStop,
                        isBelow,
                        isWait,
                    });
                    return isBelow && (isDraggable1 || isStop || isWait);
                })
                    .sort((a, b) => {
                    return (a.getBoundingClientRect().top -
                        b.getBoundingClientRect().top);
                });
                console.log(`Found ${belowElements.length} elements below START`);
                // Execute commands sequentially
                for (const element of belowElements) {
                    console.log("Executing command for:", element.id);
                    yield executeCommand(element);
                }
            }
        }));
    }
});
// ------------ Utility Functions ------------
function getElementCenter(element) {
    const rect = element.getBoundingClientRect();
    return {
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
    };
}
function isNearPosition(pos1, pos2, targetWidth, targetHeight) {
    return (Math.abs(pos1.x - pos2.x) < targetWidth &&
        Math.abs(pos1.y - pos2.y) < targetHeight);
}
function calculateSnapPosition(element, target) {
    const rect = element.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    return {
        x: targetRect.left,
        y: targetRect.top - rect.height,
    };
}
function createGhostElement(original) {
    const ghost = original.cloneNode(true);
    ghost.style.pointerEvents = "none";
    ghost.style.position = "absolute";
    ghost.classList.add("ghost");
    document.body.appendChild(ghost);
    ghostElements.push(ghost);
    return ghost;
}
function removeGhostElements() {
    ghostElements.forEach((ghost) => ghost.remove());
    ghostElements = [];
}
function checkPositionOccupied(snapPos, element, excludeIds) {
    const allDraggables = draggables
        .map((id) => document.getElementById(id))
        .filter((element) => element !== null);
    for (const otherElement of allDraggables) {
        if (excludeIds.includes(otherElement.id))
            continue;
        const otherCenter = getElementCenter(otherElement);
        if (isNearPosition({
            x: snapPos.x + element.getBoundingClientRect().width / 2,
            y: snapPos.y + element.getBoundingClientRect().height / 2,
        }, otherCenter, 32, 24)) {
            return otherElement;
        }
    }
    return null;
}
function handleElementSnapping(draggableElement, target) {
    const elementCenter = getElementCenter(draggableElement);
    const targetRect = target.getBoundingClientRect();
    const targetCenter = getElementCenter(target);
    const allDraggables = draggables
        .map((id) => document.getElementById(id))
        .filter((element) => element !== null);
    for (const element of allDraggables) {
        if (element.id === draggableElement.id)
            continue;
        console.log("Checking element:", {
            id: element.id,
            targetWidth: targetRect.width,
            targetHeight: targetRect.height,
        });
        if (isNearPosition(elementCenter, targetCenter, targetRect.width, targetRect.height)) {
            const snapPos = calculateSnapPosition(draggableElement, element);
            draggableElement.style.left = `${snapPos.x}px`;
            draggableElement.style.top = `${snapPos.y}px`;
            return true;
        }
    }
    return false;
}
function updateGhostPositions(draggingElement, targetE, mouseX, mouseY) {
    // Clear any existing timeout
    if (ghostUpdateTimeout) {
        window.clearTimeout(ghostUpdateTimeout);
    }
    // Remove existing ghosts immediately
    removeGhostElements();
    // If no valid target or dragging element, exit
    if (!targetE || !draggingElement) {
        return;
    }
    // Create the ghost position calculation
    ghostUpdateTimeout = window.setTimeout(() => {
        const elementRect = draggingElement.getBoundingClientRect();
        const targetRect = targetE.getBoundingClientRect();
        const targetCenter = getElementCenter(targetE);
        const ghostCenter = {
            x: mouseX - dragOffset.x + elementRect.width / 2,
            y: mouseY - dragOffset.y + elementRect.height / 2,
        };
        // Only create ghost if near target
        if (isNearPosition(ghostCenter, targetCenter, targetRect.width, targetRect.height)) {
            const snapPos = calculateSnapPosition(draggingElement, targetE);
            const ghost = createGhostElement(draggingElement);
            // Position ghost immediately
            ghost.style.left = `${snapPos.x}px`;
            ghost.style.top = `${snapPos.y}px`;
            ghost.classList.add("ghost-snap");
        }
    }, 16); // Reduced timeout for smoother animation
}
// function observeDraggableElement(element: HTMLElement) {
//     observer.observe(element, {
//         attributes: true,
//         attributeFilter: ['style']
//     });
// }
function resetElementPosition(element) {
    const originalPos = originalPositions.get(element.id);
    if (originalPos) {
        element.style.top = originalPos.top;
        element.style.left = originalPos.left;
        originalPositions.delete(element.id);
    }
}
function trackDraggableElement(id) {
    if (!draggables.includes(id)) {
        draggables.push(id);
        console.log("Added to draggables:", id);
        console.log("Current draggables:", draggables);
    }
}
function showMousePosition(x, y) {
    if (!positionIndicator) {
        positionIndicator = document.createElement("div");
        positionIndicator.style.position = "fixed";
        positionIndicator.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
        positionIndicator.style.color = "white";
        positionIndicator.style.padding = "4px 8px";
        positionIndicator.style.borderRadius = "4px";
        positionIndicator.style.fontSize = "12px";
        positionIndicator.style.pointerEvents = "none";
        positionIndicator.style.zIndex = "10000";
        document.body.appendChild(positionIndicator);
    }
    positionIndicator.textContent = `X: ${Math.round(x)}px, Y: ${Math.round(y)}px`;
    positionIndicator.style.left = `${x + 15}px`;
    positionIndicator.style.top = `${y + 15}px`;
}
// ------------ Event Listeners ------------
function initializeWebSocket() {
    try {
        if (socket) {
            socket.close();
            socket = null;
        }
        socket = new WebSocket("ws://" + location.host + "/prijem");
        socket.addEventListener("open", (ev) => {
            console.log("WebSocket connection opened");
        });
        socket.addEventListener("message", (ev) => {
            console.log("Received message:", ev.data);
            if (ev.data.startsWith("error:")) {
                console.error("Server error:", ev.data);
            }
        });
        socket.addEventListener("close", (ev) => {
            console.log("WebSocket connection closed with code:", ev.code, "reason:", ev.reason);
            socket = null;
            setTimeout(initializeWebSocket, 2000);
        });
        socket.addEventListener("error", (ev) => {
            console.error("WebSocket error occurred");
            if (socket) {
                socket.close();
                socket = null;
            }
        });
    }
    catch (error) {
        console.error("Error creating WebSocket:", error);
        socket = null;
        setTimeout(initializeWebSocket, 2000);
    }
}
// Initialize WebSocket on page load
document.addEventListener("DOMContentLoaded", () => {
    initializeWebSocket();
});
document.addEventListener("mousemove", (event) => {
    showMousePosition(event.clientX, event.clientY);
});
document.addEventListener("keydown", (event) => {
    if (event.key === "p") {
        // Press 'p' to toggle position indicator
        if (positionIndicator) {
            positionIndicator.remove();
            positionIndicator = null;
        }
    }
});
// Dragstart event listener
document.addEventListener("dragstart", (event) => {
    const target = event.target;
    console.log("Drag started on element:", target.id);
    if (target.classList.contains("menu-draggable")) {
        // Create new draggable from menu item
        const clone = target.cloneNode(true);
        const originalId = target.id;
        clone.id = `${originalId}-${Date.now()}`;
        trackDraggableElement(clone.id);
        // Add appropriate class based on original element
        switch (originalId) {
            case "draggable1":
                clone.classList.add("draggable1");
                break;
            case "draggable2":
                clone.classList.add("draggable2");
                break;
            case "draggable3":
                clone.classList.add("draggable3");
                break;
            case "draggable4":
                clone.classList.add("draggable4");
                break;
        }
        clone.classList.remove("menu-draggable");
        clone.style.position = "absolute";
        clone.draggable = true;
        clone.style.visibility = "hidden";
        document.body.appendChild(clone);
        if (event.dataTransfer) {
            event.dataTransfer.setData("text/plain", clone.id);
            event.dataTransfer.effectAllowed = "move";
        }
        currentDraggedElement = clone;
        dragOffset = {
            x: event.clientX - target.getBoundingClientRect().left,
            y: event.clientY - target.getBoundingClientRect().top,
        };
        // Add input validation for draggable1
        if (originalId === "draggable1") {
            const input = clone.querySelector(".number-input");
            if (input) {
                input.addEventListener("input", (e) => {
                    const target = e.target;
                    target.value = target.value.replace(/[^0-9]/g, "");
                    const num = parseInt(target.value);
                    if (num > 100)
                        target.value = "100";
                    if (num < 0)
                        target.value = "0";
                });
            }
        }
        console.log("elemnsts", draggables);
    }
    // Handle existing draggable elements
    else if (draggables.includes(target.id)) {
        console.log("Draggable element:", target);
        event.stopPropagation();
        if (event.dataTransfer) {
            event.dataTransfer.setData("text/plain", target.id);
            event.dataTransfer.effectAllowed = "move";
        }
        currentDraggedElement = target;
        dragOffset = {
            x: event.clientX - target.getBoundingClientRect().left,
            y: event.clientY - target.getBoundingClientRect().top,
        };
    }
});
// Dragenter event listener
document.addEventListener("dragenter", (event) => {
    event.preventDefault();
    if (!currentDraggedElement)
        return;
    const target = event.target;
    if (Array.from(draggables).find((item) => item === target.id) &&
        target !== currentDraggedElement) {
        targetElement = target;
        if (lastHoveredElement && lastHoveredElement !== target) {
            resetElementPosition(lastHoveredElement);
        }
        lastHoveredElement = target;
        if (!originalPositions.has(target.id)) {
            originalPositions.set(target.id, {
                top: target.style.top,
                left: target.style.left,
            });
        }
    }
});
// Dragleave event listener
document.addEventListener("dragleave", (event) => {
    event.preventDefault();
    const target = event.target;
    const relatedTarget = event.relatedTarget;
    // Remove the incorrect assignment
    if (Array.from(draggables).find((item) => item === target.id)) {
        // Check if the related target is not another draggable element
        if (!relatedTarget ||
            Array.from(draggables).find((item) => item === target.id)) {
            resetElementPosition(target);
            lastHoveredElement = null;
            targetElement = null;
        }
    }
});
// Dragover event listener
document.addEventListener("dragover", (event) => {
    event.preventDefault();
    const target = event.target;
    if (!currentDraggedElement)
        return;
    // Calculate current position of dragged element
    const draggedRect = {
        left: event.clientX - dragOffset.x,
        top: event.clientY - dragOffset.y,
    };
    showMousePosition(draggedRect.left, draggedRect.top);
    // Find potential snap targets
    const snapTargets = draggables
        .map((id) => document.getElementById(id))
        .filter((element) => element !== null)
        .filter((other) => {
        if (other === currentDraggedElement)
            return false;
        const otherRect = other.getBoundingClientRect();
        return (otherRect.bottom <= draggedRect.top ||
            otherRect.bottom >= draggedRect.top);
    })
        .map((other) => {
        const otherRect = other.getBoundingClientRect();
        const horizontalDistance = Math.abs(draggedRect.left - otherRect.left);
        const verticalDistance = Math.abs(draggedRect.top - otherRect.top);
        // console.log("horizontalDistance (dragover)", horizontalDistance);
        // console.log("verticalDistance (dragover)", verticalDistance);
        return {
            element: other,
            horizontalDistance,
            verticalDistance,
            totalDistance: horizontalDistance + verticalDistance,
        };
    })
        .filter(({ element, horizontalDistance, verticalDistance }) => {
        const otherRect = element.getBoundingClientRect();
        // console.log('horizontalDistance (filter)', horizontalDistance);
        // console.log('verticalDistance (filter)', verticalDistance);
        // console.log('otherRect.height', otherRect.height);
        return (horizontalDistance < 110 && verticalDistance < otherRect.height);
    });
    // Show threshold for closest element
    // console.log('Snap targets:', snapTargets);
    const closest = snapTargets[0];
    if (closest) {
        showThresholdArea(currentDraggedElement, closest.element);
        // console.log('Nearest element:', {
        //     id: closest.element.id,
        //     distance: closest.totalDistance
        // });
    }
    else {
        // Remove threshold indicator if no close elements
        if (thresholdIndicator) {
            thresholdIndicator.remove();
            thresholdIndicator = null;
        }
    }
});
// Drop event listener
document.addEventListener("drop", (event) => {
    // console.log("Drop event:", event);
    event.preventDefault();
    removeGhostElements();
    if (!currentDraggedElement)
        return;
    const dropX = event.clientX - dragOffset.x;
    const dropY = event.clientY - dragOffset.y;
    // Make element visible if it was from menu
    currentDraggedElement.style.visibility = "visible";
    console.log("Dropped element:", currentDraggedElement);
    // Position the element
    currentDraggedElement.style.left = `${dropX}px`;
    currentDraggedElement.style.top = `${dropY}px`;
    // Try snapping
    // if (targetElement && !handleElementSnapping(currentDraggedElement, targetElement)) {
    //     currentDraggedElement.style.left = `${dropX}px`;
    //     currentDraggedElement.style.top = `${dropY}px`;
    // }
    checkAndAdjustPositions(currentDraggedElement);
    // Reset states
    if (positionIndicator) {
        positionIndicator.remove();
        positionIndicator = null;
    }
    currentDraggedElement = null;
    lastHoveredElement = null;
    originalPositions.clear();
    nocolseelements = false;
});
// Dragend event listener
document.addEventListener("dragend", (event) => {
    removeGhostElements();
    if (positionIndicator) {
        positionIndicator.remove();
        positionIndicator = null;
    }
    currentDraggedElement = null;
    lastHoveredElement = null;
    originalPositions.clear();
});
// ------------ Observers ------------
// const observer = new MutationObserver((mutations) => {
//     mutations.forEach((mutation) => {
//         if (mutation.type === 'attributes' &&
//             mutation.attributeName === 'style') {
//             const element = mutation.target as HTMLElement;
//             if (draggables.includes(element.id)) {
//                 checkAndAdjustPositions(element);
//             }
//         }
//     });
// });
// ------------ Additional Functions ------------
function showThresholdArea(element, aboveElement) {
    // Remove existing indicator if any
    if (thresholdIndicator) {
        thresholdIndicator.remove();
    }
    // Create threshold area indicator
    thresholdIndicator = document.createElement("div");
    thresholdIndicator.style.position = "absolute";
    thresholdIndicator.style.border = "1px dashed rgba(0, 255, 0, 0.5)";
    thresholdIndicator.style.backgroundColor = "rgba(0, 255, 0, 0.1)";
    thresholdIndicator.style.pointerEvents = "none";
    // Position and size the indicator
    const aboveRect = aboveElement.getBoundingClientRect();
    thresholdIndicator.style.left = `${aboveRect.left - 20}px`;
    thresholdIndicator.style.top = `${aboveRect.top}px`;
    thresholdIndicator.style.width = `${aboveRect.width + 40}px`; // 20px on each side
    thresholdIndicator.style.height = `${aboveRect.height}px`;
    thresholdIndicator.style.zIndex = "1000";
    document.body.appendChild(thresholdIndicator);
    // Remove the indicator after 1 second
    setTimeout(() => {
        if (thresholdIndicator) {
            thresholdIndicator.remove();
            thresholdIndicator = null;
        }
    }, 1000);
}
function checkAndAdjustPositions(changedElement = null) {
    const allDraggables = draggables
        .map((id) => document.getElementById(id))
        .filter((element) => element !== null);
    // Sort elements by vertical position (top to bottom)
    allDraggables.sort((a, b) => {
        const rectA = a.getBoundingClientRect();
        const rectB = b.getBoundingClientRect();
        return rectA.top - rectB.top;
    });
    // Keep track of processed elements
    const processedElements = new Set();
    // Process dropped/changed element first
    console.log("changed element", changedElement, "nocloseelements", nocolseelements);
    if (changedElement && !nocolseelements) {
        // console.log("Processing changed element:", changedElement);
        const result = processElement(changedElement, allDraggables, processedElements, 0);
        if (!result) {
            console.error("Failed to process changed element");
            return; // Exit early if changed element couldn't be processed
        }
    }
    // Then process other elements
    for (const element of allDraggables) {
        if (!processedElements.has(element.id) && !nocolseelements) {
            processElement(element, allDraggables, processedElements);
        }
    }
    if (nocolseelements == true) {
        console.error("Některé bloky se nepodařilo správně umístit, prosím přesuňte je ručně.");
        nocolseelements = false;
    }
}
// Helper function to process individual elements
function processElement(element, allDraggables, processedElements, depth = 0) {
    if (depth > 10) {
        console.warn("Max recursion depth reached");
        return false;
    }
    const elementRect = element.getBoundingClientRect();
    const CloseElements = allDraggables
        .filter((other) => {
        if (other === element || processedElements.has(other.id))
            return false;
        const otherRect = other.getBoundingClientRect();
        return (otherRect.bottom <= elementRect.top ||
            otherRect.bottom >= elementRect.top);
    })
        .map((other) => {
        const otherRect = other.getBoundingClientRect();
        console.info("left", elementRect.left, otherRect.left);
        const horizontalDistance = Math.abs(elementRect.left - otherRect.left);
        console.info("bottom", elementRect.top, otherRect.bottom);
        const verticalDistance = Math.abs(elementRect.top - otherRect.bottom);
        console.info("element id", other.id, "\nhorizontalDistance", horizontalDistance, "\nverticalDistance", verticalDistance);
        return {
            element: other,
            horizontalDistance,
            verticalDistance,
            totalDistance: horizontalDistance + verticalDistance,
        };
    })
        .filter(({ element, horizontalDistance, verticalDistance }) => {
        const otherRect = element.getBoundingClientRect();
        return (horizontalDistance < otherRect.width && verticalDistance < otherRect.height);
    })
        .sort((a, b) => {
        // Prioritize vertical alignment over total distance
        if (Math.abs(a.horizontalDistance - b.horizontalDistance) < 10) {
            return a.verticalDistance - b.verticalDistance;
        }
        return a.totalDistance - b.totalDistance;
    });
    console.log("Processing element:", element);
    console.log("Close elements:", CloseElements);
    console.log("procesd elements", processedElements);
    if (CloseElements.length == 0) {
        nocolseelements = true;
        return false;
    }
    const closest = CloseElements[0];
    console.info("closestelement", closest);
    if (closest) {
        const closestRect = closest.element.getBoundingClientRect();
        const processedElementsInLine = Array.from(processedElements)
            .map(id => document.getElementById(id))
            .filter((el) => {
            if (!el)
                return false;
            const elRect = el.getBoundingClientRect();
            // Check if element is in the same vertical line
            return Math.abs(elRect.left - closestRect.left) < 20;
        })
            .sort((a, b) => {
            const rectA = a.getBoundingClientRect();
            const rectB = b.getBoundingClientRect();
            return rectA.top - rectB.top;
        });
        // Calculate total height of processed elements
        const processedHeight = processedElementsInLine.reduce((height, el) => {
            const elRect = el.getBoundingClientRect();
            console.log(`Adding processed element height for ${el.id}:`, elRect.height);
            return height + elRect.height;
        }, 0);
        console.log("Height calculation:", {
            elementsAbove: processedElementsInLine.map((el) => el.id),
            totalHeight: processedHeight,
        });
        // Calculate target position without any offset
        const targetPosition = {
            left: Math.round(closestRect.left - 4),
            bottom: Math.round(closestRect.bottom + processedHeight - 4), // Add small spacing
        };
        element.style.left = `${targetPosition.left}px`;
        element.style.top = `${targetPosition.bottom}px`;
        processedElements.add(element.id);
        console.log("Target position calculation:", {
            element: element.id,
            targetLeft: targetPosition.left,
            targetBottom: targetPosition.bottom,
            processedHeight,
            processedElements: Array.from(processedElements),
        });
        // Check if any element occupies the target position
        const occupyingElements = allDraggables
            .filter(other => {
            if (other === element || processedElements.has(other.id))
                return false;
            const otherRect = other.getBoundingClientRect();
            const isOccupying = Math.abs(otherRect.left - targetPosition.left) < 120 &&
                Math.abs(otherRect.top - targetPosition.bottom) < elementRect.height;
            console.info('ocupying element', {
                id: other.id,
                is: isOccupying
            });
            return isOccupying;
        })
            .sort((a, b) => {
            const rectA = a.getBoundingClientRect();
            const rectB = b.getBoundingClientRect();
            return rectA.top - rectB.top;
        });
        console.info(occupyingElements);
        // Process occupying elements in order
        for (const occupyingElement of occupyingElements) {
            console.log(`Moving occupying element ${occupyingElement.id}`);
            const success = processElement(occupyingElement, allDraggables, processedElements, depth + 1);
            if (!success) {
                console.warn(`Failed to move occupying element ${occupyingElement.id}`);
                // Continue with other elements even if one fails
                continue;
            }
        }
        const finalRect = element.getBoundingClientRect();
        console.log(`Final position for ${element.id}:`, {
            left: finalRect.left,
            top: finalRect.top,
            style: element.style.cssText
        });
        return true;
    }
    return false;
}
