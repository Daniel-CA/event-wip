# -*- coding: utf-8 -*-
# © 2016 Alfredo de la Fuente - AvanzOSC
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp.addons.sale_order_create_event.tests.\
    test_sale_order_create_event_assistant import\
    TestSaleOrderCreateEventAssistant
from openerp import fields


class TestEventRegistrationAnalytic(TestSaleOrderCreateEventAssistant):

    def setUp(self):
        super(TestEventRegistrationAnalytic, self).setUp()
        self.del_reg_model = self.env['wiz.event.delete.canceled.registration']
        self.wiz_change_model = self.env['wiz.registration.to.another.event']
        self.partner.parent_id = self.parent
        self.env['res.partner.bank'].create({
            'state': 'iban',
            'acc_number': 'ES9121000418450200051332',
            'partner_id': self.partner.parent_id.id,
            'mandate_ids': [(0, 0, {'format': 'sepa',
                                    'signature_date': fields.Date.today()})],
        })

    def test_event_track_registration_open_button(self):
        super(TestEventRegistrationAnalytic,
              self).test_event_track_registration_open_button()
        self.assertEquals(
            self.event.count_all_registrations,
            self.event.count_registrations +
            self.event.count_teacher_registrations)
        teachers = self.event.mapped('employee_registration_ids.partner_id')
        domain = [('partner_id', 'in', teachers.ids)]
        self.assertEquals(
            self.event.count_pickings,
            len(self.env['stock.picking'].search(domain)))
        result = self.event.show_teacher_pickings()
        self.assertEqual(
            result['domain'], domain, 'Error in show pickings')
        domain = [('picking_id.partner_id', 'in', teachers.ids)]
        self.assertEquals(
            self.event.count_moves,
            len(self.env['stock.move'].search(domain)))
        result = self.event.show_teacher_moves()
        self.assertEqual(
            result['domain'], domain, 'Error in show pickings')
        self.assertEquals(self.event.count_presences,
                          len(self.event.mapped('track_ids.presences')))
        result = self.event.show_all_registrations()
        domain = [('id', 'in', self.event.mapped('registration_ids').ids)]
        self.assertEqual(
            result['domain'], domain, 'Error in show event registration')
        result = self.event.show_teacher_registrations()
        domain = [('id', 'in',
                   self.event.mapped('employee_registration_ids').ids)]
        self.assertEqual(
            result['domain'], domain,
            'Error in show event teacher registrations')
        result = self.event.show_presences()
        domain = [('id', 'in', self.event.mapped('track_ids.presences').ids)]
        self.assertEqual(
            result['domain'], domain, 'Error in show event presences')
        self.assertEquals(self.event.count_all_registrations,
                          len(self.event.no_employee_registration_ids) +
                          len(self.event.employee_registration_ids))
        self.assertEquals(self.event.count_registrations,
                          len(self.event.no_employee_registration_ids))
        self.assertEquals(self.event.count_teacher_registrations,
                          len(self.event.employee_registration_ids))
        self.assertEquals(
            self.event.count_registrations +
            self.event.count_teacher_registrations,
            len(self.event.registration_ids))
        for registration in self.event.registration_ids:
            result = registration.button_registration_open()
            wiz_id = result.get('res_id')
            add_wiz = self.wiz_add_model.browse(wiz_id)
            self.assertFalse(add_wiz.create_account)
            add_wiz.onchange_partner()
        new_event = self.event.copy()
        wiz_another_vals = {
            'new_event_id': new_event.id,
        }
        registration = self.event.registration_ids[0]
        change_wiz = self.wiz_change_model.with_context(
            active_id=self.event.registration_ids[0].id).create(
            wiz_another_vals)
        change_wiz.button_change_registration_event()
        self.assertEqual(
            registration.event_id.id, new_event.id,
            'Registration not found in new event')

    def test_event_track_assistant_delete_from_event(self):
        super(TestEventRegistrationAnalytic,
              self).test_event_track_assistant_delete_from_event()
        self.assertTrue(self.event.registration_ids.filtered(
            lambda x: x.state == 'cancel'))
        del_wiz = self.del_reg_model.with_context(
            active_ids=self.event.ids).create({})
        del_wiz.delete_canceled_registration()
        self.assertFalse(self.event.registration_ids.filtered(
            lambda x: x.state == 'cancel'))
