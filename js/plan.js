var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');
var PlanView = React.createClass({
    componentDidMount: function() {
        this.loadFromServer();
    },
    loadFromServer: function() {
        var url = '/api/plan';
        $.ajax({
            url: url,
            dataType: 'json',
            cache: false,
            success: function(response) {
                this.setState({plan: response.plan});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        })
    },
    render: function() {

        var mealTimes = {//m  t   w   t   f   s   s
            'breakfast': [[], [], [], [], [], [], []],
            'lunch':     [[], [], [], [], [], [], []],
            'snack':     [[], [], [], [], [], [], []],
            'dinner':    [[], [], [], [], [], [], []]
        };

        for (var mp in this.state.plan) {
            for (var wd in mp['weekdays']) {
                mealTimes[mp['meal_time']][wd.id - 1].push(mp);
            }
        }

        console.log(this.state);
        return (
            <p>goal</p>
        );
    }
});

if (document.getElementById("plan-view")) {
    ReactDOM.render(
        <PlanView />,
        document.getElementById("plan-view")
    );
}
