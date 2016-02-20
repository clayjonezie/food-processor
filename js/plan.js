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
        return (
            <p>goal</p>
        );
    }
});

ReactDOM.render(
    <PlanView />,
    document.getElementById("plan-view")
);
