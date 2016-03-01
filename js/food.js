var React = require('react');
var ReactDOM = require('react-dom');
var main = require('./main_out');

var NutrientDataRow = React.createClass({
    getInitialState: function() {
        return {nutrientData: this.props.nutrientData};
    },
    handleValueChange: function(e) {
        var nutrientData = this.state.nutrientData;
        nutrientData.value = e.target.value;
        this.setState({nutrientData: nutrientData});
    },
    render: function() {
        return (
            <tr>
                <td>{this.state.nutrientData.description}</td>
                <td><input type="text"
                           onChange={this.handleValueChange}
                           value={this.state.nutrientData.value.toFixed(4)} /></td>
            </tr>
        );
    }
});

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
        measure.weight = e.target.value;
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

var AddFoodNutrientsForm = React.createClass({
    getInitialState: function() {
        return {amount: 0, food: null}
    },
    onFoodSelect: function(food_obj) {
        this.setState({food: food_obj});
    },
    handleAmountChange: function(e) {
        this.setState({amount: e.target.value});
    },
    onAddButtonClicked: function(e) {
        if (this.state.food == null) {
            alert("please choose a food");
            return;
        }
        this.props.addFoodNutrients(this.state.amount, this.state.food);
    },
    render: function() {
        return (
            <div className="row">
                <div className="col-md-2">
                    Add nutrients from
                </div>
                <div className="col-md-1">
                    <input type="text"
                           style={{width: "100%"}}
                           onChange={this.handleAmountChange}
                           value={this.state.amount} />
                </div>
                <div className="col-md-2">
                    grams of
                </div>
                <div className="col-md-6">
                    <main.FoodLookupField onSelect={this.onFoodSelect} />
                </div>
                <div className="col-md-1">
                    <button onClick={this.onAddButtonClicked}>Add</button>
                </div>
            </div>
        )
    }
});

var FoodEditForm = React.createClass({
    displayName: 'FoodEditForm',
    getId: function() {
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
        console.log(this.state);
        var url = '/api/food/' + this.getId();
        $.ajax(url, {
            method: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify(this.state),
            dataType: 'json',
            success: function(data) {
                if (data.success) {
                    console.log("successful send");
                } else {
                    console.log("failed send");
                }
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(url, status, err.toString());
            }.bind(this)
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
    addFoodNutrients: function(amount, food_obj) {
        console.log("adding " + amount);
        console.log(food_obj);
        var url = '/api/food/' + food_obj.id + '/nutrients'
        $.ajax(url, {
            method: 'GET',
            success: function(data) {
                var food = this.state.food;
                console.log(data.nutrients);
                for (var i in data.nutrients) {
                    var nut = data.nutrients[i];
                    var stored_nut = food.nutrients.find(function(stored_nut) {
                        return stored_nut.nutrient_id == nut.nutrient_id;
                    });
                    if (stored_nut != undefined) {
                        console.log("was " + stored_nut.value + " adding " + nut.value + " amt " + amount);
                        stored_nut.value += nut.value * amount / 100.0;
                    }
                }
                this.setState({food: food});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(url, status, err.toString());
            }
        });
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
                       <input type="submit" value="Save Changes" readOnly={true}/>
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
                       <AddFoodNutrientsForm addFoodNutrients={this.addFoodNutrients} />
                       <div className="row">
                           <table id="nutrients" className="table table-bordered">
                               <tbody>
                               <tr>
                                   <th>Nutrient</th>
                                   <th>Amount in 100g</th>
                               </tr>
                               {this.state.food.nutrients.map(function(nutrient) {
                                   return (
                                       <NutrientDataRow
                                           nutrientData={nutrient}
                                           key={nutrient.id}
                                       />
                                   );
                               }.bind(this))}
                               </tbody>
                           </table>
                       </div>
                       <input type="submit" value="Save Changes" readOnly={true}/>
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
