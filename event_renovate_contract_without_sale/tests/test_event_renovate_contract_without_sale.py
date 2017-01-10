# -*- coding: utf-8 -*-
# (c) 2017 Alfredo de la Fuente - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common


class TestEventRenovateContractWithoutSale(common.TransactionCase):

    def setUp(self):
        super(TestEventRenovateContractWithoutSale, self).setUp()
        self.account_model = self.env['account.analytic.account']
        self.wiz_model = self.env['wiz.analytic.account.renovate.contract']
        self.service_product = self.browse_ref(
            'product.product_product_consultant')
        line_vals = {'product_id': self.service_product.id,
                     'name': self.service_product.name,
                     'quantity': 1,
                     'uom_id': self.service_product.uom_id.id,
                     'price_unit': 100}
        account_vals = {'name': 'Event renovate contract without sale',
                        'date_start': '2025-01-01',
                        'date': '2025-12-31',
                        'type': 'contract',
                        'recurring_invoices': True,
                        'recurring_interval': 1,
                        'recurring_rule_type': 'monthly',
                        'recurring_next_date': '2025-01-15',
                        'recurring_invoice_line_ids': [(0, 0, line_vals)]}
        self.account = self.account_model.create(account_vals)

    def test_event_renovate_contract_withou_sale(self):
        wiz_vals = {'increase': 0.014}
        wiz = self.wiz_model.create(wiz_vals)
        wiz.with_context(
            {'active_ids': self.account.ids}).renovate_contracts()
        cond = [('name', '=', '{} {}'.format(self.account.name, '2026'))]
        account = self.account_model.search(cond, limit=1)
        self.assertNotEqual(
            len([account]), 0, 'Renovate contract without sale not found')
        self.assertEqual(
            account.date_start, '2026-01-01',
            'Error in date start of renovate contract without sale')
        self.assertEqual(
            account.date, '2026-12-31',
            'Error in date end of renovate contract without sale')
        self.assertEqual(
            self.account.recurring_next_date, account.recurring_next_date,
            'Error in recurring next date of renovate contract without sale')
        self.assertEqual(
            account.recurring_invoice_line_ids[0].price_unit, 101.4,
            'Error in price unit of renovate contract without sale')
