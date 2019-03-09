# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import datetime

class SingleVendorBill(models.TransientModel):

	_name = 'single.vendor.bill'

	# Return created vendor bills
	@api.multi
	def create_return_vendor_bill(self):
		vendor_bill_id  = self.create_single_vendor_bill()
		tree_view_ref = self.env.ref('account.invoice_supplier_tree',False)
		form_view_ref = self.env.ref('account.invoice_supplier_form',False)
		return {
					'name':'Vendor Bills',
					'res_model':'account.invoice',
					'view_type':'form',
					'view_mode':'tree,form',
					'target':'current',
					'domain':[('id','=',vendor_bill_id.id)],
					'type':'ir.actions.act_window',
					'views': [(tree_view_ref and tree_view_ref.id or False,'tree'),(form_view_ref and form_view_ref.id or False,'form')],
				}

	# Create single vendor bill from multiple orders
	@api.multi
	def create_single_vendor_bill(self):
		purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids'))
		name_orders = [order.name for order in purchase_orders]
		partners = [order.partner_id.id for order in purchase_orders]
		fiscal_positions = [order.fiscal_position_id.id for order in purchase_orders]
		not_confirmed_order = []
		for order in purchase_orders:
			if order.state != 'purchase':
				not_confirmed_order.append(order.name)
			else:
				pass
		if (len(purchase_orders)) < 2:
			raise UserError(_('Please select atleast two purchase orders to create Single Vendor Bill'))
		else:
			if(len(set(partners))!=1):
				raise UserError(_('Please select purchase orders whose "Vendors" are same to create Single Vendor Bill.'))
			else:
				if (len(set(fiscal_positions))!=1):
					raise UserError(_('Please select purchase orders whose "Fiscal Poistions" are same to create Single Vendor Bill.'))
				else:
					if any(order.state != 'purchase' for order in purchase_orders):
						raise UserError(_('Please select purchase orders which are in "Purchase Order" state to create Single Vendor Bill.%s is not confirmed yet.') % ','.join(map(str, not_confirmed_order)))
					else:   
						vendor_bill_id = self.prepare_vendor_bill()
						return vendor_bill_id

	@api.multi
	def prepare_vendor_bill(self):
		invoice_line = self.env['account.invoice.line']
		purchase_orders = self.env['purchase.order'].browse(self._context.get('active_ids'))
		name_orders = [order.name for order in purchase_orders]
		journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
		invoice_lines = []
		for order in purchase_orders:
			for line in order.order_line:
				invoice_lines.append(((0,0,{
							'name': line.name,
							'origin': line.order_id.name,
							'account_id': invoice_line.with_context({'journal_id': journal_id, 'type': 'in_invoice'})._default_account(),
							'price_unit': line.price_unit,
							'quantity': line.product_qty,
							'uom_id': line.product_uom.id,
							'product_id': line.product_id.id or False,
							'invoice_line_tax_ids': [(6, 0, line.taxes_id.ids)],
						})))
		vendor_bill_vals = {
							'name': ','.join(map(str, name_orders)),
							'origin':','.join(map(str, name_orders)),
							'date_invoice':datetime.datetime.now().date(),
							'type': 'in_invoice',
							'partner_id': order.partner_id.id,
							'invoice_line_ids': invoice_lines,
							'journal_id': journal_id,
							'comment': order.notes,
							'payment_term_id': order.payment_term_id.id,
							'fiscal_position_id': order.fiscal_position_id.id,
							'company_id': order.company_id.id,
							'user_id': order.activity_user_id and order.activity_user_id.id,
						}
		vendor_bill_id = self.env['account.invoice'].create(vendor_bill_vals)
		vendor_bill_id._onchange_invoice_line_ids()
		return vendor_bill_id