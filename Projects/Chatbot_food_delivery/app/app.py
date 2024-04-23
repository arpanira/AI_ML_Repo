from flask import Flask,request,jsonify
app=Flask(__name__)
import db_helper
import generic_helper

@app.route("/",methods=['GET','POST'])
def home():
    return "Welcome Home",200


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    payload = request.json
    intent_name = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    outputContexts=payload['queryResult']['outputContexts']

    """intent_handler_dict={"add.order:ongoing-order":add_order_handler,
                         "remove.order:ongoing-order":remove_order_handler,
                         "order.complete":complete_order_handler,
                         "track_order:ongoing-tracking":track_order_handler}

    return intent_handler_dict["intent_name"](parameters)"""

    session_id=generic_helper.extract_session_id(outputContexts[0]['name'])

    if intent_name == "track_order:ongoing-tracking":
        return track_order_handler(parameters)
    elif intent_name=="add.order:ongoing-order":
        return add_order_handler(parameters,session_id)
    elif intent_name=="order.complete":
        return order_complete_handler(parameters,session_id)
    elif intent_name=="remove.order:ongoing-order":
        return remove_order_handler(parameters, session_id)
    else:
        return jsonify({"fulfillmentText": "Intent not supported."}), 400

def  track_order_handler(parameters):
    order_id = int(parameters.get("order_id"))
    if order_id:

        order_status=db_helper.get_order_status(order_id)
        if order_status:
            return jsonify({"fulfillmentText": f"Your order status is {order_status}"})
        else:
            return jsonify({"fulfillmentText":f"Could not find status for order_id:{order_id}"})
    else:
            return jsonify({"fulfillmentText": "Please provide a valid order ID."})

inprogress_orders={}
def add_order_handler(parameters:dict,session_id:str):

    food_item=parameters.get("food_item")
    quantity=parameters.get("number")
    if len(food_item)!=len(quantity):
        return jsonify({"fulfillmentText":f"Please specify food item with their quantities"})
    else:

        new_food_dict=dict(zip(food_item,quantity))
        print('********************************************************')
        print(quantity)
        print(session_id)
        if session_id in inprogress_orders:

            #inprogress_orders[session_id].update(new_food_dict[session_id])
            inprogress_orders[session_id].update(new_food_dict)
        else:
            inprogress_orders[session_id]=new_food_dict
        order_string=generic_helper.get_string_from_food_dict(inprogress_orders[session_id])

        return jsonify({"fulfillmentText": f"We have received the order of {order_string}.Anything Else to be added?"})

def order_complete_handler(parameters:dict,session_id:str):
    if session_id not in inprogress_orders:
        return jsonify({"fulfillmentText":f"Sorry we could not find your sessionId in our system"})
    else:
        order=inprogress_orders[session_id]

        max_order_id=db_helper.get_new_order(order)
        print("New Order is ",max_order_id)

        print("Start save order")
        db_helper.save_to_db(max_order_id,order)

        total_bill=db_helper.get_bill_Amount(max_order_id)
        #Clearing the session ID for which order is generated and submitted.
        del inprogress_orders[session_id]
        return jsonify({"fulfillmentText":f"Awesome! Your Order is submitted.Your Order number is {max_order_id} and Bill Amout is {total_bill}"})

#Define a dictionary to store inprogress orders.
#InProgress_orders={"session_id_1:{"pizzas":2,samosa":1},"session_id_2:{chole":1}}

def remove_order_handler(parameters:dict,session_id:str):
    print(session_id,',',inprogress_orders)
    items_removed=[]
    food_item=parameters["food_item"]
    quantity=parameters["number"]
    order=inprogress_orders[session_id]
    for food in food_item:
        if food not in order:
            return jsonify({"fulfillmentText":f"Sorry, food item '{food}' does not exist in your order. Please check and confirm."})
            break

    # iterate through each food item,and remove the food item fully ,if quantity not specified

    if not quantity :#When quantity is empty list
        for food in food_item:
            del order[food]
            inprogress_orders[session_id].update(order)
            items_removed.append(food)
        order_string = generic_helper.get_string_from_food_dict(inprogress_orders[session_id])
        if order_string =='':
            return jsonify({"fulfillmentText": f"Your order updated.Removed items {items_removed}.Your new order is empty.Do you want to add anything ?"})
        else:
            return jsonify({"fulfillmentText": f"Your order updated.Removed items {items_removed}.Your new order is {order_string}.Anything Else?"})
        #return jsonify({"fulfillmentText":f"Your order updated.Removed items {items_removed}.Your new order is {inprogress_orders[session_id]}.Anything Else?"})

    # iterate through each food item,and remove the food item as per quantity specified.
    if quantity is not None:
        for f, q in list(zip(food_item, quantity)):
            order[f] -= q
            inprogress_orders[session_id].update(order)
        order_string = generic_helper.get_string_from_food_dict(inprogress_orders[session_id])
        return jsonify({"fulfillmentText":f"Your new order is {order_string}.Anything Else?"})
if __name__ == '__main__':
    app.run(debug=True)

