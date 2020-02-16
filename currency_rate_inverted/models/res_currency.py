# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2015 Techrifiv Solutions Pte Ltd
# Copyright 2015 Statecraft Systems Pte Ltd
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    rate_inverted = fields.Boolean(
        string='Inverted exchange rate',
        company_dependent=True,
    )

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        rate = super()._get_conversion_rate(
            from_currency,
            to_currency,
            company,
            date
        )

        if not from_currency.rate_inverted and not to_currency.rate_inverted:
            return rate
        elif from_currency.rate_inverted and to_currency.rate_inverted:
            return 1 / rate

        currency_rates = (
            from_currency + to_currency
        )._get_rates(company, date)
        l_rate = currency_rates.get(to_currency.id)
        r_rate = currency_rates.get(from_currency.id)
        if not from_currency.rate_inverted and to_currency.rate_inverted:
            return 1 / (l_rate * r_rate)
        elif from_currency.rate_inverted and not to_currency.rate_inverted:
            return l_rate * r_rate

# just to show also date in known/advertise format
    inverted_rate = fields.Float(digits=0, compute="_computed_inverted_rate",store=True, traking=True)
    @api.depends('rate')
    def _computed_inverted_rate(self):
        for record in self:
            record.inverted_rate = 1.0/ record.rate

class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"
    _name = "res.currency.rate"
#    _order = "name desc, id desc"

    inverted_rate = fields.Float(digits=0, compute="_computed_inverted_rate",store=True, traking=True)
    @api.depends('rate')
    def _computed_inverted_rate(self):
        for record in self:
            record.inverted_rate = 1.0/ record.rate
#/ just to show also date in known/advertise format
            