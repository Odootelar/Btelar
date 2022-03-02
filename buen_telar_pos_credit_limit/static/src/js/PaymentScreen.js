odoo.define('buen_telar_pos_credit_limit.UpdatePaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');


    const UpdatePaymentScreen = PaymentScreen => class extends PaymentScreen {
            async validateOrder(isForceValidate) {

            if(!this.env.pos.get_order().check_paymentlines_rounding()) {
                    const { confirmed, payload } = await this.showPopup('CreditTextInputPopup', {
                            startingValue: 'Code',
                            title: this.env._t('Credit Code ?'),
                    });
                    if (confirmed) {
                        //Buscar los catalogos por codigo
                        //Si el descuento que voy a aplicar es mayor que el limite del catalogo mensaje error.
                        this.trigger('set-numpad-mode', { mode: 'quantity' });
                        } else {
                            this.trigger('set-numpad-mode', { mode: 'quantity' });
                        }
                }



            super.validateOrder(isForceValidate)

        }
    };

    Registries.Component.extend(PaymentScreen, UpdatePaymentScreen);

    return UpdatePaymentScreen;
 });