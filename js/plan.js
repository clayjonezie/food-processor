var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');
var PlanView = React.createClass({
    getInitialState: function () {
        return {plan: []}
    },
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

        for (var i in this.state.plan) {
            var mp = this.state.plan[i];
            for (var j in mp['weekdays']) {
                var wd = mp['weekdays'][j];
                console.log('pushing ' + mp + 'to ' + mp['meal_time'] + (wd.id - 1));
                mealTimes[mp['meal_time']][wd.id - 1].push(mp);
            }
        }

        console.log(this.state.plan);
        console.log(mealTimes);

        var i = 0;
        function renderDay(day) {
            var mps = day.map(function(mp) {
                return (<li key={mp['id']}>{mp['food']['description']}</li>);
            });
            return (<td key={i++}><ul>{mps}</ul></td>);
        }

        return (
            <table className="plan table table-bordered">
                <tbody>
                    <tr><td></td><td>Monday</td><td>Tuesday</td><td>Wednesday</td><td>Thursday</td><td>Friday</td>
                        <td>Saturday</td><td>Sunday</td></tr>
                    <tr><td>Breakfast</td>{mealTimes['breakfast'].map(renderDay)}</tr>
                    <tr><td>Lunch</td>{mealTimes['lunch'].map(renderDay)}</tr>
                    <tr><td>Snacks</td>{mealTimes['snack'].map(renderDay)}</tr>
                    <tr><td>Dinner</td>{mealTimes['dinner'].map(renderDay)}</tr>
                </tbody>
            </table>
        );
    }
});

if (document.getElementById("plan-view")) {
    ReactDOM.render(
        <PlanView />,
        document.getElementById("plan-view")
    );
}
