odoo.define('casamedica_pos_discount.CreditUpdateOrderModel', function(require) {
    'use strict';

var models = require('point_of_sale.models');
var core = require('web.core');

models.load_fields('pos.order', 'credit_catalog_code');

models.load_models([{
    model:  'credit.limit.catalog',
    fields: ['name', 'id', 'code'],
    domain: [],
    loaded: function(self, credit_catalog_ids) {
        self.credit_catalog_ids = credit_catalog_ids;
    }
}]);

var posmodel_super = models.PosModel.prototype;
models.PosModel = models.PosModel.extend({
    load_server_data: function () {
        var self = this;
        return posmodel_super.load_server_data.apply(this, arguments).then(function () {
            var records = self.rpc({
                model: 'credit.limit.catalog',
                method: 'get_code_hashed',
                args: [[]],
            });
            return records.then(function (catalog_data) {
                self.credit_catalog_ids.forEach(function (catalog) {
                    var data = _.findWhere(catalog_data, {'id': catalog.id});
                    if (data !== undefined){
                        catalog.name = data.name;
                        catalog.code = data.code;
                    }
                });
            });
        });
    },
});

 });