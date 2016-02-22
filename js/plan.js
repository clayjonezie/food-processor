

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');
var main = require('./main_out');

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

// plan form
// food/measure/count, what days, what food times

var PlanAddForm = React.createClass({
    getInitialState: function() {
        return {days: [], foodTimes: []};
    },
    handleSubmit: function(e) {
        e.preventDefault();
        var mealTimes = $("#food-entry-form .mealTimes input[type='checkbox']").filter(function(i, input) {
            return input.checked;
        }).map(function(i, input) {
            return input.value;
        });
        var weekdays = $("#food-entry-form .weekdays input[type='checkbox']").filter(function(i, input) {
            return input.checked;
        }).map(function(i, input) {
            return input.value;
        });

        console.log(mealTimes);
        console.log(weekdays);
    },
    render: function() {
        return (
            <div>
                <main.FoodEntryForm />

                <form id="food-entry-form" onSubmit={this.handleSubmit}>
                    <p className="mealTimes">
                        <label><input type="checkbox" value="breakfast" />Breakfast</label>
                        <label><input type="checkbox" value="lunch" />Lunch</label>
                        <label><input type="checkbox" value="snack" />Snack</label>
                        <label><input type="checkbox" value="dinner" />Dinner</label>
                    </p>
                    <p className="weekdays">
                        <label><input type="checkbox" value="1" />Monday</label>
                        <label><input type="checkbox" value="2" />Tuesday</label>
                        <label><input type="checkbox" value="3" />Wednesday</label>
                        <label><input type="checkbox" value="4" />Thursday</label>
                        <label><input type="checkbox" value="5" />Friday</label>
                        <label><input type="checkbox" value="6" />Saturday</label>
                        <label><input type="checkbox" value="7" />Sunday</label>
                    </p>
                    <input type="submit" value="Add"/>
                </form>
            </div>
        );
    }
});

// plan page
if (document.getElementById("plan-add-form")) {
    ReactDOM.render(
        <PlanAddForm />,
        document.getElementById("plan-add-form")
    );
}

if (document.getElementById("plan-view")) {
    ReactDOM.render(
        <PlanView />,
        document.getElementById("plan-view")
    );
}

// end plan page