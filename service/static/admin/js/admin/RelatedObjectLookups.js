/*global SelectBox, interpolate*/
// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.
'use strict';
{
    const $ = django.jQuery;
    let popupIndex = 0;
    const relatedWindows = [];

    function setPopupIndex() {
        const windowName = window.name;
        const popupMatch = windowName.match(/^(change|add|delete)_(.+)_(\d+)_/i);
        if (popupMatch) {
            popupIndex = parseInt(popupMatch[3], 10);
        }
    }

    function dismissChildPopups() {
        relatedWindows.forEach(function(win) {
            if (!win.closed) {
                win.close();
            }
        });
    }

    // Replace the unload event with beforeunload
    window.addEventListener('beforeunload', function(evt) {
        window.dismissChildPopups();
    });

    $(document).ready(function() {
        setPopupIndex();
        $("a[data-popup-opener]").on('click', function(event) {
            event.preventDefault();
            opener.dismissRelatedLookupPopup(window, $(this).data("popup-opener"));
        });
        $('body').on('click', '.related-widget-wrapper-link[data-popup="yes"]', function(e) {
            e.preventDefault();
            if (this.href) {
                const event = $.Event('django:show-related', {href: this.href});
                $(this).trigger(event);
                if (!event.isDefaultPrevented()) {
                    showRelatedObjectPopup(this);
                }
            }
        });
        $('body').on('change', '.related-widget-wrapper select', function(e) {
            const event = $.Event('django:update-related');
            $(this).trigger(event);
            if (!event.isDefaultPrevented()) {
                updateRelatedObjectLinks(this);
            }
        });
        $('.related-widget-wrapper select').trigger('change');
        $('body').on('click', '.related-lookup', function(e) {
            e.preventDefault();
            const event = $.Event('django:lookup-related');
            $(this).trigger(event);
            if (!event.isDefaultPrevented()) {
                showRelatedObjectLookupPopup(this);
            }
        });
    });
}
