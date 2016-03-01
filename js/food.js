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
       this.props.onMeasureDelete(this.props.id);
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
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
        });
    },
    sendToServer: function(e) {
        e.preventDefault();
        var url = '/api/food/' + this.getId();
        $.ajax(url, {
            method: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(this.state),
            dataType: 'json'
        });
    },
    addMeasure: function() {
        var food = this.state.food;
        food.measures.push({id: 0, description: "", weight: 0});
        this.setState({food: food});
    },
    onMeasureDelete: function(id) {
        var food = this.state.food;
        food.measures = food.measures.filter(function(measure) {
            return measure.id != id;
        });
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
                                               key={measure.id}
                                               id={measure.id}
                                           />
                                       );
                                   }.bind(this))}
                               <tr>
                                   <td colSpan="3"><button onClick={this.addMeasure}>add measure</button></td>
                               </tr>
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
