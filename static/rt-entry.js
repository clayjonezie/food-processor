function addItem(foodId, quantity, measureId, textDescription) {
    var len = $("input[name^='food_ids']").length;
    var next = len;
    var $food_id_input = $('<input type="hidden" />');
    $food_id_input.attr('name', 'food_ids-' + next);
    $food_id_input.attr('value', foodId);
    var $measure_id_input = $('<input type="hidden" />');
    $measure_id_input.attr('name', 'measure_ids-' + next);
    $measure_id_input.attr('value', measureId);
    var $quantity = $('<input type="hidden" />');
    $quantity.attr('name', 'quantities-' + next);
    $quantity.attr('value', quantity);

    var $new_li = $('<li></li>');
    $new_li.append('[<a class="delete_row">x</a>] ');
    $new_li.append(textDescription);
    $new_li.append($food_id_input);
    $new_li.append($measure_id_input);
    $new_li.append($quantity);
    $('ul.rtp-entry-items').append($new_li);

    $(".delete_row").click(function() {
        $(this).parent().remove();
    });
}

$(function() {
    $('input.realtime-parse').autocomplete({
        serviceUrl: '/parse-autocomplete',
        type: 'POST',
        dataType: 'json',
	deferRequestBy: 500,
        onSearchStart: function() {
            console.log('search start');
        },
        onSearchComplete: function (query, suggestions) {
            console.log('search complete'); 
            console.log(suggestions);
        },
        onSelect: function(suggestion) {
            $('input.realtime-parse').autocomplete('clear');
            $('input.realtime-parse').val('');
            $('input.realtime-parse').focus();

            var foodId = suggestion.data['food-id'];
            var quantity = suggestion.data['quantity'];
            var measureId = suggestion.data['measure-id'];
            addItem(foodId, quantity, measureId, suggestion.value)
        },
    noCache: true
    });
    $('a.add-suggestion').click(function() {
        var $this = $(this);
        console.log($this);
        addItem($this.attr('data-foodid'), $this.attr('data-count'),
            $this.attr('data-measureid'), this.innerText);
    });
});
