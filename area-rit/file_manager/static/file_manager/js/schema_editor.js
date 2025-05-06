document.addEventListener("DOMContentLoaded", () => {
    console.log("Metadata loaded:", metadata);

    // Initialize interface
    renderTree();
    if (!selectedFile) {
        document.getElementById("overwrite").value = "false";
    }
    toggleNewFileNameField();
    onFileSelectChange();
    updateEditingTitle();

    // Event listeners
    document.getElementById("overwrite").addEventListener("change", toggleNewFileNameField);
    document.getElementById("expand-all-btn").addEventListener("click", expandAll);
    document.getElementById("collapse-all-btn").addEventListener("click", collapseAll);
    document.getElementById("save-metadata-btn").addEventListener("click", saveMetadata);
    document.getElementById("delete-file-btn").addEventListener("click", deleteFile);
    document.getElementById("create-new-schema-btn").addEventListener("click", createNewSchema);
    document.getElementById("file_name").addEventListener("change", onFileSelectChange);
});

// Global variables
let currentMetadata = metadata;

// Functions previously inlined are now extracted and organized

function updateEditingTitle() {
    const title = document.getElementById("editing-file-title");
    if (selectedFile) {
        title.textContent = "Editing: " + selectedFile;
    } else {
        title.textContent = "Saving New File";
    }
}

function renderTree() {
    const treeContainer = document.getElementById("metadata-tree");
    treeContainer.innerHTML = "";

    if (currentMetadata) {
        const rootElement = createCollapsibleTree(currentMetadata, [], true);
        treeContainer.appendChild(rootElement);
    } else {
        treeContainer.innerHTML = "<p style='text-align:center;'>No metadata loaded. Load a file or create a new schema.</p>";
    }
}

// Create a collapsible tree for the JSON
function createCollapsibleTree(data, path = [], isRoot = false) {
    const container = document.createElement("div");

    if (isRoot) {
        if (!data.children) {
            const rootControls = document.createElement("div");
            rootControls.style.marginBottom = "1vh";
            const addRootChildBtn = document.createElement("button");
            addRootChildBtn.textContent = "New node";
            addRootChildBtn.classList.add("button");
            addRootChildBtn.onclick = () => addChildNode(["children"]);
            rootControls.appendChild(addRootChildBtn);
            container.appendChild(rootControls);
        } else {
            const sortedChildren = sortChildren(data.children);
            sortedChildren.forEach((child) => {
                const item = createChildNode(child, path);
                container.appendChild(item);
            });

            // Add a button to add more children at root level
            const addRootChildContainer = document.createElement("div");
            addRootChildContainer.style.marginTop = "1vh";
            const addRootChildBtn = document.createElement("button");
            addRootChildBtn.textContent = "New node";
            addRootChildBtn.classList.add("button");
            addRootChildBtn.onclick = () => addChildNode(["children"]);
            addRootChildContainer.appendChild(addRootChildBtn);
            container.appendChild(addRootChildContainer);
        }
        return container;
    }

    // Non-root node: create metadata box
    const metadataContainer = document.createElement("div");
    metadataContainer.classList.add("metadata-box");
    metadataContainer.dataset.nodePath = path.join("."); // Store the path in a dataset attribute for later retrieval

    if (data.status) {
        metadataContainer.classList.add(data.status.toLowerCase());
    }

    ["status", "comment", "mapping"].forEach((field) => {
        if (data[field] !== undefined) {
            const line = document.createElement("div");
            line.style.marginBottom = "0.5vh";
            
            const label = document.createElement("label");
            label.textContent = `${field}: `;
            
            let input;
            if (field === "status") {
                input = document.createElement("select");
                ["required", "recommended", "optional"].forEach((option) => {
                    const optionElement = document.createElement("option");
                    optionElement.value = option;
                    optionElement.textContent = option.charAt(0).toUpperCase() + option.slice(1);
                    if (data[field] === option) {
                        optionElement.selected = true;
                    }
                    input.appendChild(optionElement);
                });
            } else {
                input = document.createElement("input");
                input.type = "text";
                input.value = data[field];
            }
            input.dataset.path = path.join(".");
            input.dataset.field = field;
            input.addEventListener('change', onFieldChange);

            line.appendChild(label);
            line.appendChild(input);
            metadataContainer.appendChild(line);
        }
    });

    container.appendChild(metadataContainer);

    if (data.children) {
        const sortedChildren = sortChildren(data.children);
        sortedChildren.forEach((child) => {
            const item = createChildNode(child, path);
            container.appendChild(item);
        });
    } else {
        const controlsContainer = document.createElement("div");
        controlsContainer.style.marginBottom = "1vh";
        const addChildBtn = document.createElement("button");
        addChildBtn.textContent = "New node";
        addChildBtn.classList.add("button");
        addChildBtn.onclick = () => addChildNode(path.concat("children"));
        controlsContainer.appendChild(addChildBtn);
        container.appendChild(controlsContainer);
    }

    return container;
}

function createChildNode(child, parentPath) {
    const { name, data, status } = child;
    const item = document.createElement("div");
    item.style.marginBottom = "1vh";

    const toggleIcon = document.createElement("span");
    toggleIcon.classList.add("toggle-icon");
    toggleIcon.textContent = "+";

    const nodePath = parentPath.concat("children", name);
    const nestedContainer = createCollapsibleTree(data, nodePath, false);
    nestedContainer.style.display = "none";
    nestedContainer.classList.add("nested");

    toggleIcon.onclick = () => {
        nestedContainer.style.display =
            (nestedContainer.style.display === "none" || nestedContainer.style.display === "") ? "block" : "none";
        toggleIcon.textContent = (toggleIcon.textContent === "+") ? "-" : "+";
    };

    const label = document.createElement("span");
    label.textContent = name;
    label.classList.add("status-label");
    label.style.color = getStatusColor(status); // Initial color based on status

    // Store the path in the label so we can easily find & update it later
    label.dataset.path = nodePath.join(".");

    const nodeControls = document.createElement("span");
    nodeControls.classList.add("node-controls");

    // Add Child
    const addChildBtn = document.createElement("button");
    addChildBtn.textContent = "New node";
    addChildBtn.classList.add("button");
    addChildBtn.onclick = () => addChildNode(nodePath.concat("children"));
    nodeControls.appendChild(addChildBtn);

    // Rename
    const renameBtn = document.createElement("button");
    renameBtn.textContent = "Rename";
    renameBtn.onclick = () => renameNode(parentPath.concat("children"), name);
    nodeControls.appendChild(renameBtn);

    // Remove
    const removeBtn = document.createElement("button");
    removeBtn.textContent = "Remove";
    removeBtn.onclick = () => removeNode(parentPath.concat("children"), name);
    nodeControls.appendChild(removeBtn);

    item.appendChild(toggleIcon);
    item.appendChild(label); // Append the label here
    item.appendChild(nodeControls);
    item.appendChild(nestedContainer);

    return item;
}

function sortChildren(children) {
    return Object.keys(children)
        .map((key) => ({
            name: key,
            data: children[key],
            status: children[key].status || "optional"
        }))
        .sort((a, b) => {
            const statusOrder = { required: 1, recommended: 2, optional: 3 };
            if (statusOrder[a.status] !== statusOrder[b.status]) {
                return statusOrder[a.status] - statusOrder[b.status];
            }
            return a.name.localeCompare(b.name);
        });
}

function getStatusColor(status) {
    switch (status.toLowerCase()) {
        case "required":
            return "red";
        case "recommended":
            return "orange";
        case "optional":
            return "green";
        default:
            return "#333";
    }
}

function onFieldChange(event) {
    const input = event.target;
    const field = input.dataset.field;        // e.g., 'status'
    const nodePath = input.dataset.path.split(".");
    let current = currentMetadata;

    // Walk down currentMetadata to the correct node
    for (let i = 0; i < nodePath.length; i++) {
        const p = nodePath[i];
        if (!current[p]) {
            current[p] = {};
        }
        current = current[p];
    }

    // Update currentMetadata
    current[field] = input.value;

    // If the field is 'status', immediately update the background and label color
    if (field === "status") {
        // 1. Update the metadata-box background class
        const metadataBox = input.closest(".metadata-box");
        if (metadataBox) {
            metadataBox.classList.remove("required", "recommended", "optional");
            if (current[field]) {
                metadataBox.classList.add(current[field].toLowerCase());
            }
        }

        // 2. Update the node name label color
        //    We look for a <span class="status-label"> with the same path
        const labelSelector = `.status-label[data.path="${nodePath.join(".")}"]`;
        // Corrected below: data-path instead of data.path

        // Important:
        // In a CSS selector, custom data attributes use a dash, not a dot. 
        // So if you store label.dataset.path = nodePath.join("."), 
        // you must select it as [data-path="some.value"], not [data.path="some.value"].
        const label = document.querySelector(`.status-label[data-path="${nodePath.join(".")}"]`);
        if (label) {
            label.style.color = getStatusColor(current[field]);
        }
    }
}

function getNodeByPath(path) {
    let node = currentMetadata;
    for (let i = 0; i < path.length; i++) {
        node = node[path[i]];
        if (!node) break;
    }
    return node;
}

function addChildNode(path) {
    const parentNode = getNodeByPath(path.slice(0, -1));
    if (!parentNode.children) {
        parentNode.children = {};
    }

    const nodeName = prompt("Enter new node name:");
    if (!nodeName || nodeName.trim() === "") return;

    if (parentNode.children[nodeName]) {
        alert("A node with that name already exists!");
        return;
    }

    parentNode.children[nodeName] = {
        "status": "required",
        "comment": "",
        "mapping": ""
    };

    renderTree();
}

function removeNode(parentPath, nodeName) {
    const parentNode = getNodeByPath(parentPath);
    if (!parentNode || !parentNode[nodeName]) return;

    const confirmDelete = confirm(`Are you sure you want to delete the node "${nodeName}" and all its children?`);
    if (!confirmDelete) return;

    delete parentNode[nodeName];
    renderTree();
}

function renameNode(parentPath, oldName) {
    const parentNode = getNodeByPath(parentPath);
    if (!parentNode || !parentNode[oldName]) return;

    const newName = prompt("Enter a new name for the node:", oldName);
    if (!newName || newName.trim() === "") return;
    if (parentNode[newName] && newName !== oldName) {
        alert("A node with that name already exists!");
        return;
    }

    if (newName !== oldName) {
        parentNode[newName] = parentNode[oldName];
        delete parentNode[oldName];
    }

    renderTree();
}

function buildJsonFromForm() {
    return currentMetadata;
}

function saveMetadata() {
    const metadataToSave = buildJsonFromForm();
    const overwrite = document.getElementById("overwrite").value === "true";
    const newFileName = document.getElementById("new_file_name").value.trim();

    if (!selectedFile && !newFileName) {
        alert("Please provide a new file name when no file is currently loaded.");
        return;
    }

    if (!overwrite && !newFileName && selectedFile) {
        alert("Please provide a new file name if you do not wish to overwrite the existing file.");
        return;
    }

    const fileNameToSave = (overwrite && selectedFile) ? selectedFile : newFileName;

    fetch(saveMetadataUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
            metadata: metadataToSave,
            file_name: fileNameToSave,
            overwrite: overwrite
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.status === "success" && !selectedFile) {
            window.location.href = homepageUrl;
        }
    })
    .catch(error => {
        console.error("Error saving metadata:", error);
        alert("Failed to save metadata. Check the console for details.");
    });
}

function toggleNewFileNameField() {
    const overwrite = document.getElementById("overwrite");
    const newFileNameContainer = document.getElementById("new-file-name-container");
    newFileNameContainer.style.display = (overwrite.value === "false") ? "block" : "none";
}

function expandAll() {
    document.querySelectorAll(".nested").forEach(nested => nested.style.display = "block");
    document.querySelectorAll(".toggle-icon").forEach(icon => icon.textContent = "-");
}

function collapseAll() {
    document.querySelectorAll(".nested").forEach(nested => nested.style.display = "none");
    document.querySelectorAll(".toggle-icon").forEach(icon => icon.textContent = "+");
}

function createNewSchema() {
    if (!confirm("This will start a new schema from scratch. Unsaved changes to the current metadata will be lost. Proceed?"))
        return;

    currentMetadata = {
        "status": "required",
        "comment": "",
        "mapping": ""
    };
    renderTree();
    document.getElementById("overwrite").value = "false";
    toggleNewFileNameField();
    updateEditingTitle();
}

function deleteFile() {
    const fileSelect = document.getElementById("file_name");
    const selectedFileName = fileSelect.value.trim();
    if (!selectedFileName) {
        alert("No file selected to delete.");
        return;
    }

    if (!confirm(`Are you sure you want to delete the file "${selectedFileName}"? This action cannot be undone.`))
        return;

    fetch(deleteFileUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({ file_name: selectedFileName })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            window.location.href = homepageUrl;
        }
    })
    .catch(error => {
        console.error("Error deleting file:", error);
        alert("Failed to delete the file. Check console for details.");
    });
}

function onFileSelectChange() {
    const fileSelect = document.getElementById("file_name");
    const deleteFileBtn = document.getElementById("delete-file-btn");
    deleteFileBtn.style.display = fileSelect.value.trim() ? "inline-block" : "none";
}
