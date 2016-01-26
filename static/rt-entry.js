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
            console.log(suggestion);
            $('ul.rtp-entry-items').append('<li>' + suggestion.value + '</li>');
            $('input.realtime-parse').autocomplete('clear');
            $('input.realtime-parse').val('');
            $('input.realtime-parse').focus();
            var len = $("input[name^='food_ids']").length;
            var next = len;
            var $food_id_input = $('<input type="hidden" />');
            $food_id_input.attr('name', 'food_ids-' + next);
            $food_id_input.attr('value', suggestion.data['food-id']);
            $("ul#food_ids").append($food_id_input);
            var $measure_id_input = $('<input type="hidden" />');
            $measure_id_input.attr('name', 'measure_ids-' + next);
            $measure_id_input.attr('value', suggestion.data['measure-id']);
            $("ul#measure_ids").append($measure_id_input);
            var $quantity = $('<input type="hidden" />');
            $quantity.attr('name', 'quantities-' + next);
            $quantity.attr('value', suggestion.data['quantity']);
            $("ul#quantities").append($quantity);
        },
        noCache: true
    });
});
