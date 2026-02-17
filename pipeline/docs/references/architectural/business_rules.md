# Business Rules Explained

In programming, a **Business Rule** is a statement that defines or constrains some aspect of the business. It is a "truth" about how the company operates, regardless of whether you are using a Python script, a spreadsheet, or a piece of paper.

Crucially, **Business Rules are independent of technology**. If you switched your database from PostgreSQL to MongoDB, or your backend from Python to Go, the Business Rule would remain exactly the same.

### The "Paper and Pen" Test
To check if a piece of logic is a Business Rule, ask yourself:
> "If I fired all the programmers and we went back to doing this job with paper, pens, and filing cabinets, would this rule still exist?"

*   **YES**: It is a Business Rule. (e.g., "We don't ship until the check clears.")
*   **NO**: It is a Technical Rule or Implementation Detail. (e.g., "The password must be hashed using Argon2" or "The API must return JSON.")

## Categories of Business Rules

Business Rules generally fall into four categories:

### 1. Fact/Structural Rules (What things are)
These define the relationships between data entities.

*   **The Rule**: "A Premium Subscription must always be linked to a valid Credit Card."
*   **Python Example**:
    ```python
    def validate_subscription(sub_type, payment_method):
        if sub_type == "PREMIUM" and not payment_method.is_credit_card():
            raise ValueError("Premium requires a credit card.")
    ```

### 2. Constraint/Validation Rules (What is allowed)
These prevent invalid states. They are often "If/Then" statements.

*   **The Rule**: "Users under 18 cannot purchase alcohol."
*   **Python Example**:
    ```python
    def can_purchase_alcohol(user_age):
        # The rule is the '18' constant, not the 'if' statement itself.
        return user_age >= 18
    ```

### 3. Action/Trigger Rules (What happens next)
These define side effects based on specific conditions.

*   **The Rule**: "If an order total exceeds $500, apply a 10% discount and notify the manager."
*   **Python Example**:
    ```python
    def process_order(order):
        if order.total > 500:
            order.apply_discount(0.10)
            manager.notify(order.id)
    ```

### 4. Derivation Rules (How to calculate)
These define how new data is created from existing data.

*   **The Rule**: "The 'Loyalty Tier' is calculated by the number of orders in the last 12 months."
*   **Python Example**:
    ```python
    def get_loyalty_tier(order_history):
        recent_orders = [o for o in order_history if o.date > one_year_ago]
        if len(recent_orders) > 50:
            return "GOLD"
        return "SILVER"
    ```

## Other "Rules" in Software

In a professional Python project (especially in Linux/DevOps environments), you will encounter other types of logic that are often confused with Business Rules.

| Logic Type | Subject | Example |
| :--- | :--- | :--- |
| **Business Rule** | The "Truth" | "Refunds are only issued within 30 days." |
| **Technical Rule**| The "Machine" | "The Docker container must restart on failure." |
| **UI Rule** | The "Visuals" | "Show the error message in red text." |
| **Data Rule** | The "Storage" | "The ID column must be an auto-incrementing integer." |

1.  **Technical/Application Rules**: Requirements for the software to function correctly but don't care about the business.
    *   *Example*: "The session token expires after 30 minutes of inactivity."
    *   *Difference*: The business owner doesn't care about "session tokens," but they do care about "Security."

2.  **Data Integrity Rules**: Database-level constraints that ensure the data isn't corrupted.
    *   *Example*: "The `email` column must be unique."
    *   *Difference*: This is a technical implementation of the business rule "A user cannot have two accounts with the same email."

3.  **Workflow/Orchestration Logic**: The "plumbing" that connects services.
    *   *Example*: "Try to charge the card 3 times before sending a failure email."
    *   *Difference*: This is a policy for how the system handles technical failure, not necessarily a fundamental truth of the business.

4.  **UI/UX Rules**: Logic that only exists to make the interface better.
    *   *Example*: "Grey out the 'Submit' button until all fields are filled."
    *   *Difference*: This is purely about the "User Experience," not the underlying business transaction.
