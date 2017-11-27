import React from 'react';
import AttackItem  from './AttackItem';
import _ from 'lodash';

export default class AttackListDetails extends React.Component {

    constructor() {
        super();
        this.state = {
            completed: [],
            runpaused: []

        }
    }

    deleted = () => {
        this.props.onReload();
    }

    createAttackItem = (attacks) => {
        return attacks.map((attack) => {
            return <AttackItem key={ attack.victim_id } attack={ attack } onReload={ this.deleted }/>;
        });
    }


    completedAttacks = () => {
        return(
            <div>
                <h2 className='btn' data-toggle='collapse' data-target='#complete'>Completed</h2>                                  
                <ul className='line collapse in' id='complete'>
                    { this.createAttackItem(this.state.completed) }
                </ul>
            </div>
        );
    }

    runpausedAttacks = () => {
        return(
            <div>
                <h2 className='btn' data-toggle='collapse' data-target='#running'>Running &amp; Paused</h2>
                <ul className='line collapse in' id='running'>
                    { this.createAttackItem(this.state.runpaused) }
                </ul>
            </div>
        );
    }

    componentDidMount() {
        if (this.props.attacks) {
            let attacks = _.partition(this.props.attacks, { state: 'completed' });
            this.setState({ completed: attacks[0], runpaused: attacks[1] });
        }
    }
	
    render() {
        return(
            <div>
                { this.state.completed.length > 0 ? this.completedAttacks(this.state.completed) : null }
                { this.state.runpaused.length > 0 ? this.runpausedAttacks(this.state.runpaused) : null }
            </div>
        );
    }
}
