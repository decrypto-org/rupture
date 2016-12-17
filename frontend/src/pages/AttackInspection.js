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

    handleVictimState(id, button){
        if (button === 'Pause') {
            this.setState({ button: 'Attack' });
        }
        else {
            this.setState({ button: 'Pause' });
        }

        axios.patch('/breach/victim/' + this.props.attack.id + '/', {
			victim_id: this.props.attack.id,
            state: this.state.attackState
        })
		.then(res => {
            console.log(res)
        })
        .catch(error => {
            console.log(error);
        });
    }
    
    handleClick = () => {
        this.setState({ showNotification: true });

    }

    onUndo = () => {
        this.setState({ showNotification: false });
    }

    onVerify = () => {
        this.setState({ showNotification: false });
        browserHistory.push('/');
    }

    getVictimDetails = () => {
        axios.get('/breach/victim/' + this.props.params.victim_id)
        .then(res => {
            this.setState({ attack: res.data });
        })
        .catch(error => {
            console.log(error);
        });
    }

    componentWillMount = () => {
        this.getVictimDetails();
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
                    <button type='button' className='btn btn-primary serialmargin' 
                        onClick={ () => this.handleVictimState(attack.id, this.state.button) }>
                        { this.state.button }
                    </button>
                </div>
            </div>
        );
    }
}
