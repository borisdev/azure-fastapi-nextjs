// Pure JavaScript implementation of the Research Report component
console.log("Research Report JS loaded");

// Get elements from the DOM
const reactRoot = document.getElementById("react-root");

// Sample research report data
const research_report = {
    health_target: "Improve your health",
    mechanisms: [
        {
            name: "Mechanism 1",
            approaches: [
                {
                    name: "Approach 1",
                    health_hacks: [
                        {
                            name: "Health Hack 1",
                            amazon_products: [
                                {
                                    name: "Product 1",
                                    description: "Description 1",
                                },
                                {
                                    name: "Product 2",
                                    description: "Description 2",
                                },
                            ],
                        },
                    ],
                },
            ],
        },
    ],
};

// Render the research report
function renderResearchReport() {
    // Check if the react-root element exists
    if (!reactRoot) {
        console.error("React root element not found");
        return;
    }

    try {
        console.log("Starting to render research report...");

        // Clear the react-root element
        reactRoot.innerHTML = "";

        // Create a container for the research report
        const container = document.createElement("div");
        container.className = "research-report border p-3 my-4 bg-light";

        // Add the health target as a heading
        const targetHeading = document.createElement("h2");
        targetHeading.textContent = research_report.health_target;
        targetHeading.className = "text-primary mb-4";
        container.appendChild(targetHeading);

        // Create a list for mechanisms
        const mechanismsList = document.createElement("div");
        mechanismsList.className = "mechanisms-list";

        // Render each mechanism
        research_report.mechanisms.forEach((mechanism, mechanismIndex) => {
            const mechanismCard = document.createElement("div");
            mechanismCard.className = "mechanism-card card mb-4";

            const mechanismHeader = document.createElement("div");
            mechanismHeader.className = "card-header bg-info text-white";
            mechanismHeader.textContent = `Mechanism: ${mechanism.name}`;
            mechanismCard.appendChild(mechanismHeader);

            const mechanismBody = document.createElement("div");
            mechanismBody.className = "card-body";

            // Render approaches for this mechanism
            mechanism.approaches.forEach((approach, approachIndex) => {
                const approachSection = document.createElement("div");
                approachSection.className =
                    "approach-section mb-3 border-bottom pb-3";

                const approachHeader = document.createElement("h4");
                approachHeader.textContent = `Approach: ${approach.name}`;
                approachHeader.className = "text-success";
                approachSection.appendChild(approachHeader);

                // Render health hacks for this approach
                approach.health_hacks.forEach((hack, hackIndex) => {
                    const hackSection = document.createElement("div");
                    hackSection.className = "hack-section ms-3 mb-2";

                    const hackHeader = document.createElement("h5");
                    hackHeader.textContent = `Health Hack: ${hack.name}`;
                    hackSection.appendChild(hackHeader);

                    // Render amazon products for this hack
                    const productsList = document.createElement("ul");
                    productsList.className = "list-group";

                    hack.amazon_products.forEach((product, productIndex) => {
                        const productItem = document.createElement("li");
                        productItem.className = "list-group-item";

                        const productName = document.createElement("strong");
                        productName.textContent = product.name;

                        const productDesc = document.createElement("p");
                        productDesc.textContent = product.description;
                        productDesc.className = "mb-0 mt-1";

                        productItem.appendChild(productName);
                        productItem.appendChild(document.createElement("br"));
                        productItem.appendChild(productDesc);

                        productsList.appendChild(productItem);
                    });

                    hackSection.appendChild(productsList);
                    approachSection.appendChild(hackSection);
                });

                mechanismBody.appendChild(approachSection);
            });

            mechanismCard.appendChild(mechanismBody);
            mechanismsList.appendChild(mechanismCard);
        });

        container.appendChild(mechanismsList);
        reactRoot.appendChild(container);

        console.log("Research report rendered successfully");
    } catch (error) {
        console.error("Error rendering research report:", error);

        // Show error in the react-root element
        if (reactRoot) {
            const errorDiv = document.createElement("div");
            errorDiv.className = "alert alert-danger";

            const errorTitle = document.createElement("h3");
            errorTitle.textContent = "Error Rendering Research Report";

            const errorMessage = document.createElement("p");
            errorMessage.textContent = error.message || "Unknown error";

            errorDiv.appendChild(errorTitle);
            errorDiv.appendChild(errorMessage);

            // Clear and add the error element
            reactRoot.innerHTML = "";
            reactRoot.appendChild(errorDiv);
        }
    }
}

// Render the report when the DOM is loaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderResearchReport);
} else {
    // DOM already loaded
    renderResearchReport();
}
