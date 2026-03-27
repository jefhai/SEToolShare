(function(window) {
    function getClipboardText(event) {
        if (event.clipboardData && event.clipboardData.getData) {
            return event.clipboardData.getData("text");
        }
        if (window.clipboardData && window.clipboardData.getData) {
            return window.clipboardData.getData("Text");
        }
        return "";
    }

    function attachCounter(textarea, options) {
        if (!textarea) {
            return;
        }

        var config = options || {};
        var maxLength = config.maxLength || 1000;
        var normalColor = config.normalColor || "#666";
        var limitColor = config.limitColor || "#b94a48";

        textarea.setAttribute("maxlength", String(maxLength));

        var counter = document.createElement("div");
        counter.style.textAlign = "right";
        counter.style.fontSize = "12px";
        counter.style.color = normalColor;
        counter.style.marginTop = "4px";

        function updateCounter() {
            if (textarea.value.length > maxLength) {
                textarea.value = textarea.value.substring(0, maxLength);
            }
            var currentLength = textarea.value.length;
            counter.textContent = currentLength + "/" + maxLength;
            counter.style.color = currentLength >= maxLength ? limitColor : normalColor;
        }

        textarea.parentNode.insertBefore(counter, textarea.nextSibling);
        textarea.addEventListener("input", updateCounter);
        textarea.addEventListener("paste", function(event) {
            var selectionStart = textarea.selectionStart || 0;
            var selectionEnd = textarea.selectionEnd || 0;
            var selectedLength = selectionEnd - selectionStart;
            var remaining = maxLength - (textarea.value.length - selectedLength);

            if (remaining <= 0) {
                event.preventDefault();
                return;
            }

            var pasteText = getClipboardText(event);
            if (pasteText.length > remaining) {
                event.preventDefault();
                var clipped = pasteText.substring(0, remaining);
                var before = textarea.value.substring(0, selectionStart);
                var after = textarea.value.substring(selectionEnd);
                textarea.value = before + clipped + after;
                var cursor = selectionStart + clipped.length;
                textarea.setSelectionRange(cursor, cursor);
                updateCounter();
            }
        });

        updateCounter();

        if (config.focus) {
            textarea.focus();
        }
    }

    function attachBySelector(selector, options) {
        var textareas = document.querySelectorAll(selector);
        for (var i = 0; i < textareas.length; i++) {
            attachCounter(textareas[i], options);
        }
    }

    window.ToolShareMessageCounter = {
        attach: attachCounter,
        attachBySelector: attachBySelector,
    };
})(window);
