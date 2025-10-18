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

const uploader = "upload-component";

document.addEventListener("DOMContentLoaded", () => {
    WaitForElements([`#${uploader}`], (UploadComponent) => {
        // Set a callback on dash-uploader, it will be called by itself when fileError event occurred.
        dash_clientside.set_props(uploader, {
            onUploadErrorCallback: (file, _) => {
                const filename = file.name;

                dash_clientside.set_props("js-new-error-file", {
                    data: {filename: filename}
                });
            }
        });

        UploadComponent.addEventListener("change", () => {
            dash_clientside.set_props("js-update-prompt", {
                data: {
                    show: true, title: "Uploading...",
                    msg: "Now files are uploading. It may take some time, so hang tight...", color: "info",
                    dismissable: false
                }
            });
            dash_clientside.set_props("js-error-file-empty-trigger", {
                data: {status: true}
            });
        });
    });
});