import React from 'react';
import { Link } from 'react-router';
import _ from 'lodash';

import GrayPc from '../img/gray_pc.png';

export default class NotStartedVictims extends React.Component {


    possibleVictims = () => {
        if (this.props.victims) {
            return _.map(this.props.victims, (victim) => {
                return(
                    <li className='scanned' key={ victim.victim_id }>
                        <Link to={{ pathname: '/attackconfig/' + victim.victim_id }}>
                            <img src={ GrayPc } alt='ghost_pc' className='pull-left nooutline' name='scanned victim'/>
                        </Link>    
                        <ul>
                            <li className='state'>Not started</li>
                            <li>{ victim.sourceip }</li>
                        </ul>
                    </li>
                );
            });
        }
    }

    render(){
        return(
            <div>
                <h2 className='btn' data-toggle='collapse' data-target='#notstarted'>Not started</h2>
                <ul className='line collapse in' id='notstarted'>
                    { this.possibleVictims() }
                </ul>
            </div>
        );
    }
}
