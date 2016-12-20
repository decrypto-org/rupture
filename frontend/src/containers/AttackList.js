import React from 'react';
import RunPausedAttacks  from './RunPausedAttacks';
import CompletedAttacks from './CompletedAttacks';

export default class AttackList extends React.Component {

    render(){ 
        return(
            <div>
                <div>
                    <h2 className='btn' data-toggle='collapse' data-target='#complete'>Completed</h2>
                    <ul className='line collapse in' id='complete'>
                        <CompletedAttacks attacks={ this.props.attacks }/>
                    </ul>
                </div>
                <div>
                    <h2 className='btn' data-toggle='collapse' data-target='#running'>Running &amp; Paused</h2>
                    <ul className='line collapse in' id='running'>
                        <RunPausedAttacks attacks={ this.props.attacks } onReload={ this.props.onReload }/>
                    </ul>
                </div>
            </div>
        );
    }
}
