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
            var len = $("input[name^='food_ids']").length;
            var next = len;
            var $food_id_input = $('<input type="hidden" />');
            $food_id_input.attr('name', 'food_ids-' + next);
            $food_id_input.attr('value', suggestion.data['food-id']);
            var $measure_id_input = $('<input type="hidden" />');
            $measure_id_input.attr('name', 'measure_ids-' + next);
            $measure_id_input.attr('value', suggestion.data['measure-id']);
            var $quantity = $('<input type="hidden" />');
            $quantity.attr('name', 'quantities-' + next);
            $quantity.attr('value', suggestion.data['quantity']);

            var $new_li = $('<li></li>');
            $new_li.append('[<a class="delete_row">x</a>] ');
            $new_li.append(suggestion.value);
            $new_li.append($food_id_input);
            $new_li.append($measure_id_input);
            $new_li.append($quantity);
            $('ul.rtp-entry-items').append($new_li);

            $(".delete_row").click(function() {
                $(this).parent().remove();
            });
        },
    noCache: true
    });
});
