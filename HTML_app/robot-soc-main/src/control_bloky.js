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
let ghostUpdateTimeout = null;
let originalPositions = new Map();
let lastHoveredElement = null;
let activeDraggable = null;
// Add this helper function for delayed execution
function executeWithDelay(element) {
    return __awaiter(this, void 0, void 0, function* () {
        return new Promise((resolve) => {
            const durationInput = element.querySelector('.duration-input');
            const duration = parseInt((durationInput === null || durationInput === void 0 ? void 0 : durationInput.value) || '1') * 1000; // Convert to milliseconds
            handleDraggable1Send(element);
            setTimeout(() => {
                resolve();
            }, duration);
        });
    });
}
// Update the executeCommand function
function executeCommand(element) {
    return __awaiter(this, void 0, void 0, function* () {
        return new Promise((resolve) => {
            const isStop = element.id.startsWith('draggable3-');
            console.log('Executing command for:', element.id, 'isStop:', isStop);
            if (isStop) {
                console.log('Found STOP element, sending stop command...');
                try {
                    const direction = 0;
                    const speed = 0;
                    const message = `stop ${direction} ${speed}`;
                    console.log('Sending message:', message);
                    if (socket) {
                        socket.send(message);
                    }
                }
                catch (error) {
                    console.error('Error sending stop message:', error);
                }
                resolve();
            }
            else {
                const durationInput = element.querySelector('.duration-input');
                const duration = parseInt((durationInput === null || durationInput === void 0 ? void 0 : durationInput.value) || '1') * 1000;
                handleDraggable1Send(element);
                setTimeout(() => {
                    resolve();
                }, duration);
            }
        });
    });
}
// Remove the duplicate click listener and update the DOMContentLoaded listener
document.addEventListener('DOMContentLoaded', () => {
    const commandButton = document.getElementById('command-button');
    if (commandButton) {
        commandButton.addEventListener('click', (event) => __awaiter(void 0, void 0, void 0, function* () {
            // Prevent event bubbling
            event.stopPropagation();
            console.log('Command button clicked, starting scan...');
            // Find START elements
            const startElements = document.querySelectorAll('[id^="draggable2-"]');
            console.log('Found START elements:', startElements.length);
            for (const startElement of Array.from(startElements)) {
                const startRect = startElement.getBoundingClientRect();
                // Find elements below START
                const belowElements = Array.from(document.querySelectorAll('.draggable1, .draggable2, .draggable3')).filter(element => {
                    const isDraggable1 = element.id.startsWith('draggable1-');
                    const isStop = element.id.startsWith('draggable3-');
                    const rect = element.getBoundingClientRect();
                    const isBelow = rect.top > startRect.bottom;
                    console.log('Checking element:', {
                        id: element.id,
                        isDraggable1,
                        isStop,
                        isBelow
                    });
                    return isBelow && (isDraggable1 || isStop);
                }).sort((a, b) => {
                    return a.getBoundingClientRect().top - b.getBoundingClientRect().top;
                });
                console.log(`Found ${belowElements.length} elements below START`);
                // Execute commands sequentially
                for (const element of belowElements) {
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
        x: rect.left + (rect.width / 2),
        y: rect.top + (rect.height / 2)
    };
}
function isNearPosition(pos1, pos2, thresholdX, thresholdY) {
    return Math.abs(pos1.x - pos2.x) < thresholdX &&
        Math.abs(pos1.y - pos2.y) < thresholdY;
}
function calculateSnapPosition(element, target) {
    const rect = element.getBoundingClientRect();
    const targetCenter = getElementCenter(target);
    return {
        x: targetCenter.x - (rect.width / 2),
        y: targetCenter.y - (rect.height * 1.5)
    };
}
function createGhostElement(original) {
    const ghost = original.cloneNode(true);
    ghost.style.pointerEvents = 'none';
    ghost.style.position = 'absolute';
    ghost.classList.add('ghost');
    document.body.appendChild(ghost);
    ghostElements.push(ghost);
    return ghost;
}
function removeGhostElements() {
    ghostElements.forEach(ghost => ghost.remove());
    ghostElements = [];
}
function checkPositionOccupied(snapPos, element, excludeIds) {
    const allDraggables = Array.from(document.querySelectorAll('.draggable1, .draggable2, .draggable3'));
    for (const otherElement of allDraggables) {
        if (excludeIds.includes(otherElement.id))
            continue;
        const otherCenter = getElementCenter(otherElement);
        if (isNearPosition({
            x: snapPos.x + (element.getBoundingClientRect().width / 2),
            y: snapPos.y + (element.getBoundingClientRect().height / 2)
        }, otherCenter, 32, 24)) {
            return otherElement;
        }
    }
    return null;
}
function handleElementSnapping(draggableElement) {
    const elementCenter = getElementCenter(draggableElement);
    const allDraggables = Array.from(document.querySelectorAll('.draggable1, .draggable2, .draggable3'));
    for (const element of allDraggables) {
        if (element.id === draggableElement.id)
            continue;
        const targetCenter = getElementCenter(element);
        if (isNearPosition(elementCenter, targetCenter, 32, 24)) {
            const snapPos = calculateSnapPosition(draggableElement, element);
            draggableElement.style.left = `${snapPos.x}px`;
            draggableElement.style.top = `${snapPos.y}px`;
            return true;
        }
    }
    return false;
}
function updateGhostPositions(draggingElement, mouseX, mouseY) {
    if (ghostUpdateTimeout) {
        window.clearTimeout(ghostUpdateTimeout);
    }
    ghostUpdateTimeout = window.setTimeout(() => {
        removeGhostElements();
        const elementRect = draggingElement.getBoundingClientRect();
        const ghostX = mouseX - dragOffset.x;
        const ghostY = mouseY - dragOffset.y;
        const allDraggables = Array.from(document.querySelectorAll('.draggable1, .draggable2, .draggable3'));
        for (const element of allDraggables) {
            if (element.id === draggingElement.id)
                continue;
            const targetCenter = getElementCenter(element);
            const ghostCenter = {
                x: ghostX + (elementRect.width / 2),
                y: ghostY + (elementRect.height / 2)
            };
            if (isNearPosition(ghostCenter, targetCenter, 32, 24)) {
                const snapPos = calculateSnapPosition(draggingElement, element);
                if (Math.abs(snapPos.x - ghostX) > 5 || Math.abs(snapPos.y - ghostY) > 5) {
                    const snappedGhost = createGhostElement(draggingElement);
                    snappedGhost.style.left = `${snapPos.x}px`;
                    snappedGhost.style.top = `${snapPos.y}px`;
                    snappedGhost.classList.add('ghost-snap');
                }
                break;
            }
        }
    }, 16);
}
function observeDraggableElement(element) {
    observer.observe(element, {
        attributes: true,
        attributeFilter: ['style']
    });
}
function resetElementPosition(element) {
    const originalPos = originalPositions.get(element.id);
    if (originalPos) {
        element.style.top = originalPos.top;
        element.style.left = originalPos.left;
        originalPositions.delete(element.id);
    }
}
// Update handleDraggable1Send function
function handleDraggable1Send(element) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.error('WebSocket is not open');
        initializeWebSocket();
        return;
    }
    const directionSelect = element.querySelector('.direction-select');
    const input = element.querySelector('.number-input');
    if (!directionSelect || !input) {
        console.error('Required elements not found in', element);
        return;
    }
    try {
        const direction = directionSelect.value || 'vpred';
        const speed = Math.min(Math.max(parseInt(input.value || '0'), 0), 100);
        const message = `start ${direction} ${speed}`;
        console.log('Sending message:', message);
        socket.send(message);
    }
    catch (error) {
        console.error('Error sending message:', error);
    }
}
// ------------ Event Listeners ------------
function initializeWebSocket() {
    try {
        if (socket) {
            socket.close();
            socket = null;
        }
        socket = new WebSocket(`ws://${window.location.hostname}:5000/prijem`);
        socket.addEventListener("open", (ev) => {
            console.log("WebSocket connection opened");
        });
        socket.addEventListener("message", (ev) => {
            console.log("Received message:", ev.data);
            if (ev.data.startsWith('error:')) {
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
document.addEventListener('DOMContentLoaded', () => {
    initializeWebSocket();
});
// Dragstart event listener
document.addEventListener('dragstart', (event) => {
    const target = event.target;
    if (target.classList.contains('menu-draggable')) {
        // Create new draggable from menu item
        const clone = target.cloneNode(true);
        const originalId = target.id;
        // Add appropriate class based on original element
        switch (originalId) {
            case 'draggable1':
                clone.classList.add('draggable1');
                break;
            case 'draggable2':
                clone.classList.add('draggable2');
                break;
            case 'draggable3':
                clone.classList.add('draggable3');
                break;
        }
        clone.id = `${originalId}-${Date.now()}`;
        clone.classList.remove('menu-draggable');
        clone.style.position = 'absolute';
        clone.draggable = true;
        clone.style.visibility = 'hidden';
        document.body.appendChild(clone);
        if (event.dataTransfer) {
            event.dataTransfer.setData('text/plain', clone.id);
            event.dataTransfer.effectAllowed = 'move';
        }
        currentDraggedElement = clone;
        dragOffset = {
            x: event.clientX - target.getBoundingClientRect().left,
            y: event.clientY - target.getBoundingClientRect().top
        };
        // Add input validation for draggable1
        if (originalId === 'draggable1') {
            const input = clone.querySelector('.number-input');
            if (input) {
                input.addEventListener('input', (e) => {
                    const target = e.target;
                    target.value = target.value.replace(/[^0-9]/g, '');
                    const num = parseInt(target.value);
                    if (num > 100)
                        target.value = '100';
                    if (num < 0)
                        target.value = '0';
                });
            }
        }
    }
    // Handle existing draggable elements
    else if (target.classList.contains('draggable1') ||
        target.classList.contains('draggable2') ||
        target.classList.contains('draggable3')) {
        event.stopPropagation();
        if (event.dataTransfer) {
            event.dataTransfer.setData('text/plain', target.id);
            event.dataTransfer.effectAllowed = 'move';
        }
        currentDraggedElement = target;
        dragOffset = {
            x: event.clientX - target.getBoundingClientRect().left,
            y: event.clientY - target.getBoundingClientRect().top
        };
    }
});
// Dragenter event listener
document.addEventListener('dragenter', (event) => {
    event.preventDefault();
    if (!currentDraggedElement)
        return;
    const target = event.target;
    if ((target.classList.contains('draggable1') ||
        target.classList.contains('draggable2') ||
        target.classList.contains('draggable3')) &&
        target !== currentDraggedElement) {
        if (lastHoveredElement && lastHoveredElement !== target) {
            resetElementPosition(lastHoveredElement);
        }
        lastHoveredElement = target;
        if (!originalPositions.has(target.id)) {
            originalPositions.set(target.id, {
                top: target.style.top,
                left: target.style.left
            });
        }
        checkAndAdjustPositions();
    }
});
// Dragleave event listener
document.addEventListener('dragleave', (event) => {
    event.preventDefault();
    const target = event.target;
    const relatedTarget = event.relatedTarget;
    if (target.classList.contains('draggable1') ||
        target.classList.contains('draggable2') ||
        target.classList.contains('draggable3')) {
        if (!(relatedTarget === null || relatedTarget === void 0 ? void 0 : relatedTarget.classList.contains('draggable'))) {
            resetElementPosition(target);
            lastHoveredElement = null;
        }
    }
});
// Dragover event listener
document.addEventListener('dragover', (event) => {
    event.preventDefault();
    if (!currentDraggedElement)
        return;
    updateGhostPositions(currentDraggedElement, event.clientX, event.clientY);
});
// Drop event listener
document.addEventListener('drop', (event) => {
    event.preventDefault();
    removeGhostElements();
    if (!currentDraggedElement)
        return;
    const dropX = event.clientX - dragOffset.x;
    const dropY = event.clientY - dragOffset.y;
    // Make element visible if it was from menu
    currentDraggedElement.style.visibility = 'visible';
    // Position the element
    currentDraggedElement.style.left = `${dropX}px`;
    currentDraggedElement.style.top = `${dropY}px`;
    // Try snapping
    if (!handleElementSnapping(currentDraggedElement)) {
        currentDraggedElement.style.left = `${dropX}px`;
        currentDraggedElement.style.top = `${dropY}px`;
    }
    // Ensure element is in document
    if (!document.body.contains(currentDraggedElement)) {
        document.body.appendChild(currentDraggedElement);
    }
    observeDraggableElement(currentDraggedElement);
    checkAndAdjustPositions();
    // Reset states
    currentDraggedElement = null;
    lastHoveredElement = null;
    originalPositions.clear();
});
// Dragend event listener
document.addEventListener('dragend', (event) => {
    removeGhostElements();
    currentDraggedElement = null;
    lastHoveredElement = null;
    originalPositions.clear();
});
// ------------ Observers ------------
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' &&
            mutation.attributeName === 'style') {
            const element = mutation.target;
            if (element.classList.contains('draggable1') ||
                element.classList.contains('draggable2') ||
                element.classList.contains('draggable3')) {
                checkAndAdjustPositions(element);
            }
        }
    });
});
// ------------ Additional Functions ------------
function checkAndAdjustPositions(changedElement = null) {
    const allDraggables = Array.from(document.querySelectorAll('.draggable1, .draggable2, .draggable3'));
    const processed = new Set(); // Gap between stacked elements
    // Sort elements by vertical position to process from bottom to top
    allDraggables.sort((a, b) => {
        const rectA = a.getBoundingClientRect();
        const rectB = b.getBoundingClientRect();
        return rectB.top - rectA.top;
    });
    allDraggables.forEach((element) => {
        if (changedElement && element.id === changedElement.id)
            return;
        if (processed.has(element.id))
            return;
        const elementRect = element.getBoundingClientRect();
        let stackHeight = elementRect.height;
        allDraggables.forEach((otherElement) => {
            if (element.id === otherElement.id || processed.has(otherElement.id))
                return;
            const otherRect = otherElement.getBoundingClientRect();
            // Check if elements are aligned horizontally
            if (Math.abs(elementRect.left - otherRect.left) < 32) {
                // Check if elements are close enough vertically
                if (Math.abs(elementRect.top - otherRect.top) < 24) {
                    // Move the other element up by the accumulated stack height
                    otherElement.style.left = `${elementRect.left}px`;
                    otherElement.style.top = `${elementRect.top - stackHeight}px`;
                    processed.add(otherElement.id);
                    // Increase stack height for next element
                    stackHeight += otherRect.height;
                }
            }
        });
    });
}
