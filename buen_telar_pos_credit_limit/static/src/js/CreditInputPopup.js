odoo.define('buen_telar_pos_credit_limit.CreditTextInputPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const TextInputPopup = require('point_of_sale.TextInputPopup');
    const Registries = require('point_of_sale.Registries');

    // formerly TextInputPopupWidget
    class CreditTextInputPopup extends TextInputPopup {
        constructor() {
            super(...arguments);
//            this.credit = useRef('discount');
        }
    }

//    CreditTextInputPopup.template = 'CreditTextInputPopup';
    CreditTextInputPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Credit Code',
        body: '',
        startingValue: 'Code',
    };

    Registries.Component.add(CreditTextInputPopup);

    return CreditTextInputPopup;
});