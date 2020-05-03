$(function(){
    
    let datePicker = document.getElementById("datePicker");
    let picker = new Lightpick({
        field: datePicker,
        onSelect: function(date){
            datePicker.value = date.format('Do MMMM YYYY');
        }
    })});