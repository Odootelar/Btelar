odoo.define('buen_telar_pos_credit_limit.UpdatePaymentScreen', function(require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require('web.custom_hooks');


    const UpdatePaymentScreen = PaymentScreen => class extends PaymentScreen {
            async validateOrder(isForceValidate) {

            const client_id = this.currentOrder.get_client() ? this.currentOrder.get_client().id : false;
            // verificar si esta defindo el cliente en la orden
            if(client_id) {
                // verificar si el cliente tiene credito
                let result = await this.rpc({
                                            model: 'res.partner',
                                            method: 'search_read',
                                            domain: [['id', '=', client_id]],
                                            fields: ['credit_available','sale_verify_credit'],
                                            });

                let credit_available = result[0].credit_available
                let sale_verify_credit = result[0].sale_verify_credit
                // si no tiene credito se muestra la ventana para autorizar
                console.log(this.currentOrder);
                if (credit_available === 0 && sale_verify_credit===true) {
                    const { confirmed, payload } = await this.showPopup('CreditTextInputPopup', {
                                                            startingValue: '',
                                                            title: this.env._t('Introduzca el codigo'),});
                    // se debe verificar que el codigo introducido este permitido en ese pos
                    const pos_id = this.env.pos.pos_session.config_id[0]; // id del pos.config activo
                    console.log(pos_id,payload);
                    let pos_result = await this.rpc({
                                                    model: 'pos.config',
                                                    method: 'es_valido',
                                                    args: [pos_id,payload],
                                                    });
                        console.log(pos_result);
                        if (pos_result){
                            // Si el codigo esta autoizado en el pos se valida la orden y se
                            // actualiza el pos.order con el codigo introducido
                            await super.validateOrder(isForceValidate);
                            const order = this.env.pos.get_order();
                            const serverId = this.env.pos.validated_orders_name_server_id_map[order.name];
                            if (!serverId) {
                                this.showPopup('ErrorPopup',{
                                                            title: this.env._t('Unsynced order'),
                                                            body: this.env._t('This order is not yet synced to server. Make sure it is synced then try again.'),
                                                            });
                                return;
                                }

                            if (payload) {
                                await this.rpc({
                                                model: 'pos.order',
                                                method: 'set_credit_limit_code',
                                                args: [serverId,payload],
                                                });
                                                return;
                                }
                        }else{
                             this.showPopup('ErrorPopup', {
                                title: this.env._t('Error'),
                                body: this.env._t('El codigo no esta autorizado en ese punto de venta.'),
                            });
                        }
                    }else{
                        // si tiene credito sigue el flujo normal
                        super.validateOrder(isForceValidate);
                    }
                }else{
                    // si no tiene cliente la orden sigue el flujo normal
                    super.validateOrder(isForceValidate);
                }


        }
    };

    Registries.Component.extend(PaymentScreen, UpdatePaymentScreen);

    return UpdatePaymentScreen;
 });
