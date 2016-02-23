

var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');
var main = require('./main_out');

var PlanView = React.createClass({
    refresh: function() {
        this.loadFromServer();
    },
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
                mealTimes[mp['meal_time']][wd.id - 1].push(mp);
            }
        }

        var i = 0;
        function renderDay(day) {
            var mps = day.map(function(mp) {
                return (<li key={mp['id']}>{mp['food']['description']}</li>);
            });
            return (<td key={i++}><ul>{mps}</ul></td>);
        }

        return (
            <div className="row"><div className="col-md-12">
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
            </div></div>
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
        var mealTime = $("#plan-add-form .mealTime input[type='radio']:checked").val();

        if (mealTime==null) {
            alert("Please select a meal time.")
            return;
        }
        var weekdays = $("#plan-add-form .weekdays input[type='checkbox']").filter(function(i, input) {
            return input.checked;
        }).map(function(i, input) {
            return input.value;
        }).get();

        console.log(weekdays, mealTime);

        var fefState = this.refs.FoodEntryForm.state;

        if (fefState.food == null) {
            alert("Please choose a food");
            return;
        }

        var url = '/api/plan/add';
        $.ajax({
            url: url,
            type: 'post',
            dataType: 'json',
            cache: false,
            data: {weekdays: weekdays, mealTime: mealTime, food: fefState.food,
                   count: fefState.count, measure_id: fefState.measure_id},
            success: function (data) {
                this.props.onRefresh();
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    render: function() {
        return (
            <div>
                <form id="plan-add-form" className="section" onSubmit={this.handleSubmit}>
                    <div className="row">
                        <main.FoodEntryForm ref="FoodEntryForm"/>
                    </div>
                    <div className="row"><div className="col-md-12">
                        <h4>Goal Meal Time</h4>
                    </div></div>
                    <div className="row">
                        <div className="mealTime col-md-12">
                            <div className="radio-inline"><label><input type="radio" name="mealtime" value="breakfast" />Breakfast</label></div>
                            <div className="radio-inline"><label><input type="radio" name="mealtime" value="lunch" />Lunch</label></div>
                            <div className="radio-inline"><label><input type="radio" name="mealtime" value="snack" />Snack</label></div>
                            <div className="radio-inline"><label><input type="radio" name="mealtime" value="dinner" />Dinner</label></div>
                        </div>
                    </div>
                    <div className="row"><div className="col-md-12">
                        <h4>Goal Meal Weekdays</h4>
                    </div></div>
                    <div className="row">
                        <div className="weekdays col-md-12">
                            <div className="checkbox-inline"><label><input type="checkbox" value="1" />Monday</label></div>
                            <div className="checkbox-inline"><label><input type="checkbox" value="2" />Tuesday</label></div>
                            <div className="checkbox-inline"><label><input type="checkbox" value="3" />Wednesday</label></div>
                            <div className="checkbox-inline"><label><input type="checkbox" value="4" />Thursday</label></div>
                            <div className="checkbox-inline"><label><input type="checkbox" value="5" />Friday</label></div>
                            <div className="checkbox-inline"><label><input type="checkbox" value="6" />Saturday</label></div>
                            <div className="checkbox-inline"><label><input type="checkbox" value="7" />Sunday</label></div>
                        </div>
                    </div>
                    <div className="row"><div className="col-md-12">
                        <input type="submit" value="Add"/>
                    </div></div>
                </form>
            </div>
        );
    }
});

if (document.getElementById("plan-view")) {
    var planView = ReactDOM.render(
        <PlanView />,
        document.getElementById("plan-view")
    );
    ReactDOM.render(
        <PlanAddForm onRefresh={planView.refresh} />,
        document.getElementById("plan-add-form")
    );
}

