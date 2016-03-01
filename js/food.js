var React = require('react');
var ReactDOM = require('react-dom');
var Moment = require('moment');
var d3 = require('d3');
var main = require('./main_out');

var MeasureRow = React.createClass({
    getInitialState: function() {
        return {measure: this.props.measure};
    },
    onDelete: function() {
        console.log("deleting number " + this.props.i);
       this.props.onMeasureDelete(this.props.i);
    },
    handleDescriptionChange: function(e) {
        var measure = this.state.measure;
        measure.description = e.target.value;
        this.setState({measure: measure});
    },
    handleWeightChange: function(e) {
        var measure = this.state.measure;
        measure.weight = parseFloat(e.target.value);
        this.setState({measure: measure});
    },
    render: function() {
        return (
            <tr>
                <td><input type="text"
                           value={this.state.measure.description}
                           onChange={this.handleDescriptionChange}
                /></td>
                <td><input type="text"
                           onChange={this.handleWeightChange}
                           value={this.state.measure.weight} /></td>
                <td><button onClick={this.onDelete}>delete</button></td>
            </tr>
        );
    }
});

var FoodEditForm = React.createClass({
    displayName: 'FoodEditForm',
    getId: function() {
        console.log(parseInt(window.location.hash.split("#")[1]));
        return parseInt(window.location.hash.split("#")[1]);
    },
    getInitialState: function () {
        return { food: null };
    },
    componentDidMount: function() {
        this.loadFromServer();
    },
    loadFromServer: function() {
        var url = '/api/food/' + this.getId();
        $.ajax(url, {
            method: 'GET',
            success: function(data) {
                this.setState({food: data.food});
                console.log(data.food);
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    shouldComponentUpdate: function(nextProps, nextState) {
        console.log("new state for parent");
        console.log(nextState);
        return true;
    },
    sendToServer: function(e) {
        e.preventDefault();
        console.log("in send to server...");
        console.log(this.state);
        //var url = '/api/food/' + this.getId();
        //$.ajax(url, {
        //    method: 'POST',
        //    contentType: 'application/json; charset=utf-8',
        //    data: JSON.stringify(this.state),
        //    dataType: 'json'
        //});
    },
    onMeasureDelete: function(i) {
        var food = this.state.food;
        food.measures.splice(i, 1);
        this.setState({food: food});
    },
    handleDescriptionChange: function(e) {
        var food = this.state.food;
        food.description = e.target.value;
        this.setState({food: food});
    },
    render: function () {
        console.log(this.state);
        if (this.state.food == null) {
            return (
                <p>loading</p>
            );
        } else {
            return (
                <div>
                   <form id="food-form" onSubmit={this.sendToServer}>
                       <input type="submit" value="submit" readOnly={true}/>
                       <div className="row">
                           <h2>Name:
                               <input id="description"
                                      type="text"
                                      value={this.state.food.description}
                                      onChange={this.handleDescriptionChange}
                               />
                           </h2>
                       </div>
                       <div className="row">
                           <table id="measures" className="table table-bordered">
                               <tbody>
                                   <tr>
                                       <th>Name of Measure</th>
                                       <th>Weight (grams) of measure</th>
                                       <th></th>
                                   </tr>
                                   {this.state.food.measures.map(function(measure, i) {
                                       return (
                                           <MeasureRow
                                               onMeasureDelete={this.onMeasureDelete}
                                               measure={measure}
                                               key={i}
                                               i={i}
                                           />
                                       );
                                   }.bind(this))}
                               </tbody>
                           </table>
                       </div>

                   </form>

                </div>
            );
        }
    }
});

if (document.getElementById("food-edit-form")) {
    ReactDOM.render(
        <FoodEditForm />,
        document.getElementById("food-edit-form")
    );
}
