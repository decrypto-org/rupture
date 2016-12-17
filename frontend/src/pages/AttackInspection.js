import React from 'react';
import { browserHistory} from 'react-router';
import DeleteNotification from '../containers/DeleteNotification';
import AttackDetails from '../containers/AttackDetails';
import axios from 'axios';

export default class AttackInspection extends React.Component {

	constructor() {
        super();
        this.state = {
            showNotification: false,
            attack: {},
            button: 'Pause'
        };
    }
    
    handleClick = () => {
        this.setState({ showNotification: true });

    }

    onUndo = () => {
        this.setState({ showNotification: false });
    }

    onVerify = () => {
        this.setState({ showNotification: false });
    }

    render() {
        let attack = this.state.attack
        return(
            <div className='container'>
                <AttackDetails attack={ this.state.attack }/>
                <div className='deletepause'>
                    <button type='button' className='btn btn-danger serialmargin' onClick={ () => this.handleClick(attack.id) }>Delete</button>
                    { this.state.showNotification ? <DeleteNotification onUndo={ () => this.onUndo(attack.id) }
                        onClose={ this.onVerify } /> : null }
                    <button type='button' className='btn btn-primary serialmargin' >
                        { this.state.button }
                    </button>
                </div>
            </div>
        );
    }
}
