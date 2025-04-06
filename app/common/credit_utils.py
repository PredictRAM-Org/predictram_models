from fastapi import HTTPException
from .database import get_database
from bson.objectid import ObjectId
import datetime

def get_user(db, user_id):
    if not user_id or not isinstance(user_id, str):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    user = db.investors.find_one({"_id":ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_model_credit(user):
    return user.get("model_credit", 0)

def log_transaction(db, user_id, model_name, amount, tx_type, description=""):
    tx = {
        "user": ObjectId(user_id),
        "modelName": model_name,
        "description": description,
        "type": tx_type,  # "CREDIT" or "DEBIT"
        "amount": amount,
        "createdAt": datetime.datetime.now(datetime.timezone.utc),
        "updatedAt": datetime.datetime.now(datetime.timezone.utc)
    }
    db.ModelCreditTransaction.insert_one(tx)

def check_and_deduct_credit(user_id, model_name, required_credits=1, description="Used model prediction"):
    db = get_database()
    user = get_user(db, user_id)
    available_credits = get_model_credit(user)

    if available_credits >= required_credits:
        # Deduct the required credits
        result =db.investors.update_one(
            {"_id": ObjectId( user_id)},
            {"$inc": {"model_credit": -required_credits}}
        )

        # Log the debit transaction
        log_transaction(
            db=db,
            user_id=user_id,
            model_name=model_name,
            amount=required_credits,
            tx_type="DEBIT",
            description=description
        )

        return True
    else:
        raise HTTPException(status_code=402, detail=f"Insufficient model credits. Required: {required_credits}, Available: {available_credits}")

