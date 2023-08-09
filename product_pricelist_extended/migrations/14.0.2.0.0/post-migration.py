from openupgradelib import openupgrade


"""
NOTE: This migration script is not complete and does not cover every single possibility, only those we have encountered.
It is HIGHLY advised to review the code and test it before using it in production. The original code for this
module can be found at product_pricelist_extended
"""

def create_filters_from_price_categories(env):
    env.cr.execute(
        """SELECT ppc.name, ppc.id, array_agg(pt.id)
        FROM product_price_category ppc
        LEFT JOIN product_price_category_product_template_rel m ON m.product_price_category_id = ppc.id
        LEFT JOIN product_template pt ON pt.id = m.product_template_id
        GROUP BY 1, 2 ORDER BY 1"""
    )
    tmpl_filter_ids = {}
    cat_filter_ids = {}
    create_vals_list = []
    items_to_unlink = []
    # Create price_category filters
    for price_category_name, category_id, template_ids in env.cr.fetchall():
        if not template_ids:
            continue
        template_ids = tuple(sorted(template_ids))
        if template_ids in tmpl_filter_ids:
            continue
        elif category_id in cat_filter_ids:
            continue
        else:
            filter_id = env['ir.filters'].create({
                'name': price_category_name,
                'model_id': 'product.template',
                'domain': "[('id', 'in', [%s])]" % ",".join(map(str, template_ids)),
                'is_assortment': True,
            })
            tmpl_filter_ids[template_ids] = filter_id.id
            cat_filter_ids[category_id] = filter_id.id
    # Create assortment pricelist items from old categories
    env.cr.execute(
        """SELECT
            id,
            applied_on,
            min_quantity,
            date_start,
            date_end,
            compute_price,
            currency_id,
            fixed_price,
            percent_price,
            base,
            base_pricelist_id,
            price_discount,
            price_surcharge,
            price_round,
            price_min_margin,
            price_max_margin,
            pricelist_id,
            price_categ_id
            FROM product_pricelist_item
            WHERE price_categ_id IS NOT NULL
            ORDER BY 1
        """
    )
    for row in env.cr.dictfetchall():
        create_vals = row.copy()
        del create_vals['id']
        del create_vals['price_categ_id']
        create_vals['applied_on'] = '1_product'
        if row['price_categ_id'] in cat_filter_ids:
            create_vals['assortment_filter_id'] = cat_filter_ids[row['price_categ_id']]
        else:
            continue
        create_vals_list.append(create_vals)
        items_to_unlink.append(row['id'])
    # Create assortment pricelist items from old templates
    env.cr.execute(
        """SELECT
            pricelist_item_id,
            array_agg(tmpl_id) as tmpl_ids
            FROM pricelist_item_tmpl_rel
            GROUP BY 1 ORDER BY 1
        """
    )
    for pricelist_item_id, tmpl_ids in env.cr.fetchall():
        if len(tmpl_ids) == 1:
            env['product.pricelist.item'].browse(pricelist_item_id).write({'product_tmpl_id': tmpl_ids[0]})
            continue
        if not tmpl_ids:
            continue
        tmpl_ids = tuple(sorted(tmpl_ids))
        if tmpl_ids in tmpl_filter_ids:
            filter_id = tmpl_filter_ids[tmpl_ids]
        else:
            filter_id = env['ir.filters'].create({
                'name': 'Assortment: %s' % ', '.join(env['product.template'].browse(tmpl_ids).mapped('name')),
                'model_id': 'product.template',
                'domain': "[('id', 'in', [%s])]" % ','.join(map(str, tmpl_ids)),
                'is_assortment': True,
            }).id
            tmpl_filter_ids[tmpl_ids] = filter_id
        env.cr.execute(
            """SELECT
            applied_on,
            min_quantity,
            date_start,
            date_end,
            compute_price,
            currency_id,
            fixed_price,
            percent_price,
            base,
            base_pricelist_id,
            pricelist_id,
            price_discount,
            price_surcharge,
            price_round,
            price_min_margin,
            price_max_margin
            FROM product_pricelist_item
            WHERE id = %s
        """ % pricelist_item_id)
        create_vals = env.cr.dictfetchone()
        create_vals['applied_on'] = '1_product'
        create_vals['assortment_filter_id'] = filter_id
        create_vals_list.append(create_vals)
        items_to_unlink.append(pricelist_item_id)
    # Create assortment pricelist items from old products
    product_filter_ids = {}
    env.cr.execute(
        """SELECT pricelist_item_id, array_agg(prod_id) as product_ids FROM pricelist_item_product_rel GROUP BY 1 ORDER BY 1"""
    )
    for pricelist_item_id, product_ids in env.cr.fetchall():
        if len(product_ids) == 1:
            env['product.pricelist.item'].write({'product_id': product_ids[0]})
        product_ids = tuple(sorted(product_ids))
        if product_ids in product_filter_ids:
            filter_id = product_filter_ids[product_ids]
        else:
            filter_id = env['ir.filters'].create({
                'name': 'Assortment %s' % ', '.join(env['product.product'].browse(product_ids).mapped('default_code')),
                'model_id': 'product.product',
                'domain': "[('id', 'in', [%s])]" % ','.join(map(str, product_ids)),
                'is_assortment': True,
            }).id
            product_filter_ids[product_ids] = filter_id
        env.cr.execute(
            """SELECT
            applied_on,
            min_quantity,
            date_start,
            date_end,
            compute_price,
            currency_id,
            fixed_price,
            percent_price,
            base,
            base_pricelist_id,
            pricelist_id,
            price_discount,
            price_surcharge,
            price_round,
            price_min_margin,
            price_max_margin
            FROM product_pricelist_item
            WHERE id = %s
        """ % pricelist_item_id)
        create_vals = env.cr.dictfetchone()
        create_vals['applied_on'] = '0_product_variant'
        create_vals['assortment_filter_id'] = filter_id
        create_vals_list.append(create_vals)
        items_to_unlink.append(pricelist_item_id)
    # Categories with inclusions/exclusions
    env.cr.execute(
        """SELECT id, categ_id, code_inclusion, code_exclusion
        FROM product_pricelist_item
        WHERE code_inclusion IS NOT NULL or code_exclusion IS NOT NULL
    """)
    code_filters = {}
    for pricelist_item_id, categ_id, code_inclusion, code_exclusion in env.cr.fetchall():
        key = categ_id, code_inclusion or 'X', code_exclusion or 'X'
        if key in code_filters:
            filter_id = code_filters[key]
        else:
            domain = [('categ_id', '=', categ_id)]
            name = env['product.category'].browse(categ_id).name
            if code_inclusion:
                domain.append(('default_code', 'ilike', code_inclusion))
                name += ' (Includes: %s)' % code_inclusion
            if code_exclusion:
                domain.append(('default_code', 'not ilike', code_exclusion))
                name += ' (Excludes: %s)' % code_exclusion
            filter_id = env['ir.filters'].create({
                'name': 'Assortment %s' % name,
                'model_id': 'product.product',
                'domain': str(domain),
                'is_assortment': True,
            }).id
            code_filters[key] = filter_id
        env.cr.execute(
            """SELECT
            applied_on,
            min_quantity,
            date_start,
            date_end,
            compute_price,
            currency_id,
            fixed_price,
            percent_price,
            base,
            base_pricelist_id,
            pricelist_id,
            price_discount,
            price_surcharge,
            price_round,
            price_min_margin,
            price_max_margin
            FROM product_pricelist_item
            WHERE id = %s
        """ % pricelist_item_id)
        create_vals = env.cr.dictfetchone()
        create_vals['applied_on'] = '0_product_variant'
        create_vals['assortment_filter_id'] = filter_id
        create_vals_list.append(create_vals)
        items_to_unlink.append(pricelist_item_id)
    env['product.pricelist.item'].browse(items_to_unlink).unlink()
    env['product.pricelist.assortment.item'].create(create_vals_list)
    env['product.pricelist'].cron_assortment_update()
    env.cr.execute("""
    ALTER TABLE product_pricelist_item
    DROP COLUMN code_inclusion,
    DROP COLUMN code_exclusion,
    DROP COLUMN price_categ_id
    """)
    env.cr.execute("""DROP TABLE product_price_category_product_template_rel, product_price_category_product_product_rel, product_price_category, pricelist_item_product_rel, pricelist_item_tmpl_rel""")


@openupgrade.migrate()
def migrate(env, version):
    create_filters_from_price_categories(env)
