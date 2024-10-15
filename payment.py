
import stripe 
from flask import Blueprint, request, render_template, jsonify, redirect, session, url_for, current_app

stripe.api_key = "sk_test_tR3PYbcVNZZ796tH88S4VQ2u"
stripe_blueprint = Blueprint('stripe_blueprint', __name__)

# stripe.checkout.Session.create(
#   mode="payment",
#   line_items=[{"price": "{{PRICE_ID}}", "quantity": 1}],
#   payment_intent_data={
#     "application_fee_amount": 123,
#     "transfer_data": {"destination": "{{CONNECTED_ACCOUNT_ID}}"},
#   },
#   success_url="https://example.com/success",
#   cancel_url="https://example.com/cancel",
# )

@stripe_blueprint.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        
        price_id = request.form.get('price_id')  
        connected_account_id = request.form.get('connected_account_id')
        print(price_id,connected_account_id,"price")

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            payment_intent_data={
                "application_fee_amount": 123,  
                "transfer_data": {
                    "destination": connected_account_id,
                },
            },
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),   
        )
       
        return redirect(session.url, code=303)

    except Exception as e:
        return jsonify(error=str(e)), 500
    
@stripe_blueprint.route('/success')
def success():
    return "Payment successful!"


@stripe_blueprint.route('/cancel')
def cancel():
    return "Payment canceled."