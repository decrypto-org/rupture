import React from 'react';
import { Modal } from 'react-modal-bootstrap';
import { Form } from 'react-bootstrap';
import { browserHistory } from 'react-router';
import axios from 'axios';
import CreateTarget from './CreateTarget';
import VictimIP from './VictimIP';
import _ from 'lodash';

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

    enumerateTargets = () => {
        return _.map(this.state.targets, (target) => {
            return(<option key={ target.id } value={ target.name }> { target.name } </option>);
        })
    }

    showLoadingIndicator = () => {
        return(
            <p className='notification'> Attack is getting initialized </p>
        );
    }

    componentDidMount() {
        this.setState({
            sourceip: this.props.sourceip,
        });
        axios.get('/breach/target')
        .then(res => {
            if (res.data.targets.length > 0) {
                this.setState({ targets: res.data.targets, targetName: res.data.targets[0].name })
            }
            else {
                this.setState({ showModal: true })
            }
        })
        .catch(error => {
            console.log(error);
        });
    }

    handleSubmit = (event) => {
        event.preventDefault();
        let data;
        if (this.props.victim_id === '') {
            data = {
                sourceip: this.state.sourceip,
                target: this.state.targetName
            }
        }
        else {
            data = {
                sourceip: this.state.sourceip,
                id: this.props.victim_id,
                target: this.state.targetName
            }
        }
        this.setState({ loading: true });
        axios.post('/breach/attack', data)
        .then(res => {
            console.log(res);
            browserHistory.push('/');
        })
        .catch(error => {
            console.log(error);
        });
    }

    handleIp = (ip) => {
        this.setState({ sourceip: ip });
    }

    handleTarget = () => {
        if (this.refs.targetName.value === 'new') {
            this.setState({ showModal: true });
        }
        this.setState({ targetName: this.refs.targetName.value });
    }

    createForm = () => {
        return(
            <div>
                <Form onSubmit={ this.handleSubmit }>
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
