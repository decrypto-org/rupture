import React from 'react';
import ConfigForm from '../containers/ConfigForm';

export default class AttackConfig extends React.Component {
    constructor() {
        super();
        this.state = {
            sourceip: '',
            victim_id: ''
        };
    }
    
    componentWillMount() {
        if (this.props.location.state) {
            this.setState({ sourceip: this.props.location.state.sourceip,
                            victim_id: this.props.location.state.victim_id});
        }
    }

    render() {
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
