$(document).ready(function() {
    // Code to initialize the screen when the page loads
  
    // Function to retrieve the procedure types from the server and display them in the UI
    function loadProcedureTypes() {
      $.ajax({
        url: '/procedure_types',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
          // Code to update the UI with the retrieved data
        },
        error: function() {
          // Code to display an error message to the user
        }
      });
    }
  
    // Code to bind event handlers to UI elements
    $('#add-procedure-type-form').submit(function(event) {
      event.preventDefault();
  
      // Code to validate user input and submit it to the server using an AJAX call
    });
  
    $('#delete-procedure-type-button').click(function() {
      // Code to handle the user clicking the delete button
    });
  
    // Code to call the loadProcedureTypes function to initialize the UI
    loadProcedureTypes();
  });
  