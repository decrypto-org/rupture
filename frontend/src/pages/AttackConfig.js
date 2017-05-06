import React from 'react';
import axios from 'axios';

import ConfigForm from '../containers/ConfigForm';

export default class AttackConfig extends React.Component {
    constructor() {
        super();
        this.state = {
            sourceip: '',
            victim_id: ''
        };
    }
    
    componentWillMount = () => {
        if (this.props.params.id) {
            this.setState({ victim_id: this.props.params.id });
            axios.get('/breach/victim/' + this.props.params.id)
            .then(res => {
                this.setState({ sourceip: res.data.victim_ip });
            })
            .catch(error => {
                console.log(error);
            });
        }
    }

    render() {
        console.log(this.state.sourceip);
        return(
            <div className='container'>
                <div className='row ghost formformat'>
                    <div className='col-md-offset-3 col-md-6'>
                        <ConfigForm sourceip={ this.state.sourceip } victim_id={ this.state.victim_id }/>
                    </div>
                </div>
            </div>
        );
    }
}
