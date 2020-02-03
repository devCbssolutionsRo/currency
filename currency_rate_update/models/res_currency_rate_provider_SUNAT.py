# Copyright 2009 Camptocamp
# Copyright 2009 Grzegorz Grzelak
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from datetime import date, timedelta
import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResCurrencyRateProviderSUNAT(models.Model):
    _inherit = 'res.currency.rate.provider'

    service = fields.Selection(
        selection_add=[('SUNAT', 'SUNAT')],
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != 'SUNAT':
            return super()._get_supported_currencies()  # pragma: no cover

        # List of currencies obrained from:
        # https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip
        return \
            [
                'USD'
            ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != 'SUNAT':
            return super()._obtain_rates(base_currency, currencies, date_from,
                                         date_to)  # pragma: no cover

        # This provider only serves EUR-to-??? exchange rates
        if base_currency != 'PEN':  # pragma: no cover
            raise UserError(_(
                'European Central Bank is suitable only for companies'
                ' with EUR as base currency!'
            ))

        # Depending on the date range, different URLs are used
        
        days = date_to - date_from
        if days.days < 0:
            raise UserError(_('The end date must be greater than the date from'))
        
        res = defaultdict(dict)
        for day in range(days.days+1):
            date = date_from + timedelta(day)
            response = requests.get('http://api.grupoyacck.com/tipocambio/sunat/%s/'%date.isoformat())
            if response.status_code == 200:
                data = response.json()
                rate = data.get('rates',[])
                if not rate:
                    continue
                res[data.get('date')][rate[0].get('name')] = rate[0].get('sale_value')
        return res


