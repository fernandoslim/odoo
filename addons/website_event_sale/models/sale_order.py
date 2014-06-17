# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _

# defined for access rules
class sale_order(osv.Model):
    _inherit = "sale.order"

    def _cart_find_product_line(self, cr, uid, ids, product_id=None, line_id=None, linked_line_id=None, optional_product_ids=None, context=None):
        for so in self.browse(cr, uid, ids, context=context):
            
            domain = [('order_id', '=', so.id), ('product_id', '=', product_id)]
            if line_id:
                domain += [('id', '=', line_id)]
            elif context.get("event_ticket_id"):
                domain += [('event_ticket_id', '=', context.get("event_ticket_id"))]
            domain += linked_line_id and [('linked_line_id', '=', linked_line_id)] or [('linked_line_id', '=', False)]
            if not line_id:
                if optional_product_ids:
                    domain += [('option_line_ids.product_id', '=', pid) for pid in optional_product_ids]
                else:
                    domain += [('option_line_ids', '=', False)]

            order_line_id = None
            order_line_ids = self.pool.get('sale.order.line').search(cr, SUPERUSER_ID, domain, context=context)
            if order_line_ids:
                order_line_id = order_line_ids[0]
            return order_line_id

    def _website_product_id_change(self, cr, uid, ids, order_id, product_id, line_id=None, context=None):
        values = super(sale_order,self)._website_product_id_change(cr, uid, ids, order_id, product_id, line_id=None, context=None)

        event_ticket_id = None
        if context.get("event_ticket_id"):
            event_ticket_id = context.get("event_ticket_id")
        elif line_id:
            line = self.pool.get('sale.order.line').browse(cr, SUPERUSER_ID, line_id, context=context)
            if line.event_ticket_id:
                event_ticket_id = line.event_ticket_id.id
        else:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if product.event_ticket_ids:
                event_ticket_id = product.event_ticket_ids[0]

        if event_ticket_id:
            ticket = self.pool.get('event.event.ticket').browse(cr, uid, event_ticket_id, context=context)
            if product_id != ticket.product_id.id:
                raise osv.except_osv(_('Error!'),_("The ticket doesn't match with this product."))

            values['product_id'] = ticket.product_id.id
            values['event_id'] = ticket.event_id.id
            values['event_ticket_id'] = ticket.id
            values['price_unit'] = ticket.price
            values['name'] = "%s: %s" % (ticket.event_id.name, ticket.name)

        return values
