odoo.define("erp_pos_amount_words.number_to_words", function (require) {
    var models = require('point_of_sale.models');

    var _super_pos_order = models.Order.prototype;
    models.Order = models.Order.extend({
        get_unidades: function(unidad) {
            var unidades = Array('UN ','DOS ','TRES ' ,'CUATRO ','CINCO ','SEIS ','SIETE ','OCHO ','NUEVE ');
            return unidades[unidad - 1];
        },
        get_decenas: function(decena, unidad) {
            var diez = Array('ONCE ','DOCE ','TRECE ','CATORCE ','QUINCE' ,'DIECISEIS ','DIECISIETE ','DIECIOCHO ','DIECINUEVE ');
            var decenas = Array('DIEZ ','VEINTE ','TREINTA ','CUARENTA ','CINCUENTA ','SESENTA ','SETENTA ','OCHENTA ','NOVENTA ');

            if (decena ==0 && unidad == 0) {
                return "";
            }

            if (decena == 0 && unidad > 0) {
                return this.get_unidades(unidad);
            }

            if (decena == 1) {
                if (unidad == 0) {
                    return decenas[decena -1];
                } else {
                    return diez[unidad -1];
                }
            } else if (decena == 2) {
                if (unidad == 0) {
                    return decenas[decena -1];
                }
                else if (unidad == 1) {
                    return veinte = "VEINTI" + "UNO";
                }
                else {
                    return veinte = "VEINTI" + this.get_unidades(unidad);
                }
            } else {

                if (unidad == 0) {
                    return decenas[decena -1] + " ";
                }
                if (unidad == 1) {
                    return decenas[decena -1] + " Y " + "UNO";
                }

                return decenas[decena -1] + " Y " + this.get_unidades(unidad);
            }
        },

        get_centenas: function(centena, decena, unidad) {
            var centenas = Array( "CIENTO ", "DOSCIENTOS ", "TRESCIENTOS ", "CUATROCIENTOS ","QUINIENTOS ","SEISCIENTOS ","SETECIENTOS ", "OCHOCIENTOS ","NOVECIENTOS ");

            if (centena == 0 && decena == 0 && unidad == 0) {
                return "";
            }
            if (centena == 1 && decena == 0 && unidad == 0) {
                return "CIEN ";
            }

            if (centena == 0 && decena == 0 && unidad > 0) {
                return this.get_unidades(unidad);
            }

            if (decena == 0 && unidad == 0) {
                return centenas[centena - 1]  +  "" ;
            }

            if (decena == 0) {
                var numero = centenas[centena - 1] + "" + this.get_decenas(decena, unidad);
                return numero.replace(" Y ", " ");
            }
            if (centena == 0) {

                return  this.get_decenas(decena, unidad);
            }

            return centenas[centena - 1]  +  "" + this.get_decenas(decena, unidad);

        },
        get_unidadesdemillar: function(unimill, centena, decena, unidad) {
            var numero = this.get_unidades(unimill) + " MIL " + this.get_centenas(centena, decena, unidad);
            numero = numero.replace("UN  MIL ", "MIL " );
            if (unidad == 0) {
                return numero.replace(" Y ", " ");
            } else {
                return numero;
            }
        },
        get_decenasdemillar: function(decemill, unimill, centena, decena, unidad) {
            var numero = this.get_decenas(decemill, unimill) + " MIL " + this.get_centenas(centena, decena, unidad);
            return numero;
        },
        get_centenasdemillar: function(centenamill,decemill, unimill, centena, decena, unidad) {
            var numero = 0;
            numero = this.get_centenas(centenamill,decemill, unimill) + " MIL " + this.get_centenas(centena, decena, unidad);
            return numero;
        },
        get_separar_split: function(texto){
            var contenido = new Array();
            for (var i = 0; i < texto.length; i++) {
                contenido[i] = texto.substr(i,1);
            }
            return contenido;
        },

        get_amount_text: function(cantidad) {
             var numero = 0;
            cantidad = parseFloat(cantidad);

            if (cantidad == "0.00" || cantidad == "0") {
                return "CERO con 00/100 ";
            } else {
                var ent = cantidad.toString().split(".");
                var arreglo = this.get_separar_split(ent[0]);
                var longitud = arreglo.length;

                switch (longitud) {
                    case 1:
                        numero = this.get_unidades(arreglo[0]);
                        break;
                    case 2:
                        numero = this.get_decenas(arreglo[0], arreglo[1]);
                        break;
                    case 3:
                        numero = this.get_centenas(arreglo[0], arreglo[1], arreglo[2]);
                        break;
                    case 4:
                        numero = this.get_unidadesdemillar(arreglo[0], arreglo[1], arreglo[2], arreglo[3]);
                        break;
                    case 5:
                        numero = this.get_decenasdemillar(arreglo[0], arreglo[1], arreglo[2], arreglo[3], arreglo[4]);
                        break;
                    case 6:
                        numero = this.get_centenasdemillar(arreglo[0], arreglo[1], arreglo[2], arreglo[3], arreglo[4], arreglo[5]);
                        break;
                }

                ent[1] = isNaN(ent[1]) ? '00' : ent[1];
                if (ent[1].length == 1){
                    ent[1] += '0';
                }

                return numero + " PESOS " + ent[1] + "/100";
            }

        },
        initialize: function (attributes, options) {
            _super_pos_order.initialize.apply(this, arguments);
            return this;
        },
        export_for_printing: function () {
            let receipt = _super_pos_order.export_for_printing.apply(this, arguments);
            _.extend(receipt, {
                'amount_text': this.get_amount_text(this.get_total_with_tax().toFixed(2)),

            });
            return receipt;
        },

    });

});