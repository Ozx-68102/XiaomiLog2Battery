/**
 * Wait for React Elements loaded.
 * @param {string[]} selectors
 * @param {callback} callback
 */
function WaitForElements(selectors, callback) {
    const observer = new MutationObserver((mutations) => {
        const elements = selectors.map((selector) => document.querySelector(selector));
        if (elements.every((ele) => ele !== null)) {
            observer.disconnect();
            callback(...elements);
        }
    });

    observer.observe(document.body, {childList: true, subtree: true});
}

WaitForElements(
    ["#upload-component"],
    (UploadComponent) => {
        UploadComponent.addEventListener("change", () => {
            dash_clientside.set_props("js-update-prompt", {
                data: {
                    show: true, msg: "Now files are uploading. It may take some time, so hang tight..."
                }
            });
        });
    }
);