(function($) {
    'use strict';
    $(document).ready(function() {
        var customerSelect = $('#id_customer');
        var instrumentSelect = $('#id_instrument');
        var entitlementSelect = $('#id_entitlement');
        var createdByField = $('#id_created_by');

        // Make created_by field readonly
        createdByField.prop('readonly', true);

        function updateInstruments(customerId) {
            if (!customerId) {
                instrumentSelect.empty();
                instrumentSelect.append($('<option value="">---------</option>'));
                // Clear entitlements when no customer is selected
                entitlementSelect.empty();
                entitlementSelect.append($('<option value="">---------</option>'));
                return;
            }

            $.getJSON('/admin/service/instrument/ajax/filter/', {
                'customer': customerId
            }).done(function(data) {
                var currentValue = instrumentSelect.val();
                instrumentSelect.empty();
                instrumentSelect.append($('<option value="">---------</option>'));
                
                data.forEach(function(item) {
                    var option = $('<option></option>')
                        .attr('value', item.id)
                        .text(item.serial_number);
                    if (item.id === currentValue) {
                        option.attr('selected', 'selected');
                    }
                    instrumentSelect.append(option);
                });

                // Update entitlements if an instrument is selected
                if (instrumentSelect.val()) {
                    updateEntitlements(instrumentSelect.val());
                }
            });
        }

        function updateEntitlements(instrumentId) {
            if (!instrumentId) {
                entitlementSelect.empty();
                entitlementSelect.append($('<option value="">---------</option>'));
                return;
            }

            $.getJSON('/admin/service/entitlement/ajax/filter/', {
                'instrument': instrumentId
            }).done(function(data) {
                var currentValue = entitlementSelect.val();
                entitlementSelect.empty();
                entitlementSelect.append($('<option value="">---------</option>'));
                
                data.forEach(function(item) {
                    var option = $('<option></option>')
                        .attr('value', item.id)
                        .text(`${item.entitlement_type} (${item.remaining} remaining)`);
                    if (item.id === currentValue) {
                        option.attr('selected', 'selected');
                    }
                    entitlementSelect.append(option);
                });
            });
        }

        customerSelect.on('change', function() {
            updateInstruments($(this).val());
        });

        instrumentSelect.on('change', function() {
            updateEntitlements($(this).val());
        });

        // Initial load if customer is selected
        if (customerSelect.val()) {
            updateInstruments(customerSelect.val());
        }
    });
})(django.jQuery);
