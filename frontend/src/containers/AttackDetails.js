import React from 'react';
import Logo from '../img/logo.png';
import Website from '../img/website.png';
import _ from 'lodash';


export default class AttackDetails extends React.Component {

    showTableDetails(details) {
        if (details) {
            return _.map(details, (details_row) => {
                return(
                    <tr key={ (details_row.round, details_row.batch) }>
                        <td>{ details_row.round }</td>
                        <td>{ details_row.batch }</td>
                        <td>{ details_row.alignmentalphabet }</td>
                        <td>{ details_row.possible_knownprefix }</td>
                        <td>{ details_row.confidence }</td>
                    </tr>
                );
            });
        }
    }

    render() {
        const attack = this.props.attack;
        let progressStyle = {
            width: attack.percentage
        }                 
        let imgsrc, progressClass;

        if (attack.state === 'completed') {
            progressClass = 'progress-bar progress-bar-success progress-bar-striped';
        }
        else if ((attack.state  === 'paused') || (attack.state  === 'running')) {
            progressClass = 'progress-bar progress-bar-info progress-bar-striped active';
        }

        if (attack.target_name  === 'ruptureit') {
            imgsrc = Logo;
        }
        else {
            imgsrc = Website;
        }
        return(
            <div>
                <div className='row ghost formformat'>
                    <div className='col-md-offset-4 col-md-4 centralise col-xs-offset-3 col-xs-6'>
                        <div>
                            <img src={ imgsrc } alt='target logo'/>
                            <h2>{ attack.target_name }</h2>
                        </div>
                        <p><span className='bold ip'>{ attack.victim_ip }</span></p>
                        <p className='bold decr'>Decrypted secret: { attack.known_secret } </p>
                        <div className='progress progressbar'>
                            <div className={ progressClass } style={ progressStyle }>
                                { attack.percentage }
                            </div>
                        </div>
                    </div>
                </div>

                <div className='row'>
                    <div className='col-md-offset-2 col-md-8 col-xs-offset-1 col-xs-6'>
                        <table className='table table-bordered ghost'>
                            <thead>
                                <tr>
                                    <th>Round</th>
                                    <th>Batch</th>
                                    <th>Alignment Alphabet</th>
                                    <th>Possible Knownprefix</th>
                                    <th>Confidence</th>
                                </tr>
                            </thead>
                            <tbody>
                                { this.showTableDetails(attack.attack_details) }
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        );
	}
}
