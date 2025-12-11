$(document).ready(function (){
    
    // ✅ Function to calculate and display the user's new balance after entering an amount to send
    function CalculateBalance() {
        // ✅ Get the currently logged-in user's available balance (injected from Django)
        let available_balance = "{{ request.user.account.account_balance }}" // User's current balance from backend
        
        // ✅ Get references to HTML elements by their IDs
        let new_balance = document.getElementById("new_balance")       // Element to show new balance
        let sendAmount_input = document.getElementById("amount-send")  // Input field for amount user wants to send
        let sendAmount = sendAmount_input.value                        // Value entered by user (as string)
        let errorDiv = document.getElementById("error-div")            // Div for displaying errors (if any)
        let total_to_pay = document.getElementById("total-to-pay")     // Element to show total amount user will send
        let note = document.getElementById("note")     // Element to show total amount user will send


        // ✅ Create an empty array to store validation errors (currently unused)
        let errors = []

        // ✅ Calculate new balance (subtract the entered amount from available balance)
        new_bal = available_balance - sendAmount
        //console.log(new_bal) // Print result to console (for debugging)

        // ✅ Display the updated balance in a nicely formatted way with thousand separators
        // Example: "New Balance $4,523"
        new_balance.innerHTML = `New Balance: <b> $${new_bal.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")} </b>`;

        // ✅ Display the total amount user wants to send, formatted with commas
        total_to_pay.innerHTML = `USD <b> $${sendAmount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")} </b>`;

        // ✅ If the new balance would be negative, show warning and highlight balance in red
        if (new_bal < 0) {
            new_balance.style.color = "red"  // Show red color to indicate problem
            // alert("You can only send $" + available_balance.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ","))
            note.innerHTML = `Note: You can only spend amount in your balance.`;

        } 
        // ✅ Otherwise, keep normal color (e.g., dark blue)
        else {
            new_balance.style.color = "#27276e"
        }
    }

})

            