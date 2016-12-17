import React from 'react';
import { Modal } from 'react-modal-bootstrap';
import { Form } from 'react-bootstrap';
import axios from 'axios';
import CreateTarget from './CreateTarget';
import VictimIP from './VictimIP';
import EnumerateTargets from './EnumerateTargets';

export default class ConfigForm extends React.Component {

    constructor() {
        super();

        this.state = {
            showModal: false,
            loading: false,
            sourceip: '',
            targetName: '',
            targets: []
        };
    }

    componentWillReceiveProps(nextProps) {
        this.setState({ sourceip: nextProps.sourceip });
    }

    closeModal = () => {
        this.setState({ showModal: false });
    }

    handleTarget = () => {
        if (this.refs.targetName.value === 'new') {
            this.setState({ showModal: true });
        }
        this.setState({ targetName: this.refs.targetName.value });
    }

    handleIp = (ip) => {
        this.setState({ sourceip: ip });
    }

    createForm = () => {
        return(
            <div>
				<Form>
                    <div className='form-group'>
                        <div className='row'>
                            <label htmlFor='sel1' className='col-md-4 col-sm-6 attackpagefields'> Choose Target:</label>
                            <div className='col-md-6 progressmargin'>
                                <select className='form-control' ref='targetName' value={ this.state.targetName }
                                    onChange={ this.handleTarget }>
                                    { this.enumerateTargets() }
                                    <option key='new' value='new'>Create new target</option>
                                </select>
                            </div>
                            <VictimIP sourceip={ this.state.sourceip } onUpdate={ this.handleIp }/>
                        </div>
                        <div className='col-md-4'> </div>
                        <div className='col-md-6 zeropad'>
                            <input type='submit' className='btn btn-primary attack' value='Attack'/>
                        </div>
                        { this.state.loading ? this.showLoadingIndicator() : null }
                    </div>
                </Form>

                <Modal isOpen={ this.state.showModal } onRequestHide={ this.closeModal }>
                    <CreateTarget onClose={ this.closeModal } onUpdate={ this.handleTarget }/>
                </Modal>
            </div>
        );
    }

    render() {
        return(
            <div>
                { this.createForm() }
            </div>
        );
    }
}
