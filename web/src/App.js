import React from 'react';
import axios from 'axios';
import _ from 'lodash';
import fileDownload from 'js-file-download';

import {
  Input,
  Card,
  Segment,
  Container,
  Message,
  Header,
  Icon,
} from 'semantic-ui-react';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      keyword: String,
      limit: 20,
      options: [true, true, true, true, true, true, true],
      mails: [],
      loading: false,
      message: {
        visible: false,
        color: 'red',
        header: '',
        content: '',
      },
      searchTypingTimeout: 0,
    };
  }

  onInputChange = (e) => {
    this.setState({ keyword: e.target.value });
    if (this.state.searchTypingTimeout) {
      clearTimeout(this.state.searchTypingTimeout);
    }
    this.setState({
      searchTypingTimeout: setTimeout(() => {
        this.search();
      }, 500),
    });
  };

  search = () => {
    this.setState({ loading: true });
    axios
      .post('/search', {
        keyword: this.state.keyword,
        limit: this.state.limit,
        options: this.state.options,
      })
      .then(async (res) => {
        console.log(res.data);
        this.setState({ loading: false });
        this.setState({ mails: res.data });
      })
      .catch((err) => {
        console.log(err);
        this.setState({ loading: false });
        this.showMessage('red', 'Failed to query', err.toString());
      });
  };

  downloadMail = (path) => {
    axios
      .post(`/download`, { path })
      .then((res) => {
        fileDownload(res.data, 'download.eml');
      })
      .catch((err) => {
        console.log(err);
        this.showMessage('red', 'Failed to download EML file', err.toString());
      });
  };

  showMessage = (color, header, content) => {
    this.setState({
      message: {
        visible: true,
        color,
        header,
        content,
      },
    });
  };

  closeMessage = () => {
    let { message } = this.state;
    message.visible = false;
    this.setState({ message });
  };

  renderBlank() {
    return (
      <Segment placeholder>
        <Header icon>
          <Icon name="x" />
          No satisfied items.
        </Header>
      </Segment>
    );
  }

  renderMailList() {
    const { mails } = this.state;
    if (mails.length === 0) {
      return this.renderBlank();
    }
    return _.map(
      mails,
      ({ id, path, subject, sender, receiver, date, content }) => {
        return (
          <Card fluid={true} key={id} onClick={() => this.downloadMail(path)}>
            <Card.Content>
              <Card.Header content={subject} />
              <Card.Meta content={`From ${sender} to ${receiver} on ${date}`} />
              <Card.Description content={content} />
            </Card.Content>
          </Card>
        );
      }
    );
  }

  renderMessage() {
    const { message } = this.state;
    if (message.visible) {
      return (
        <Message
          color={message.color}
          header={message.header}
          content={message.content}
          onDismiss={this.closeMessage}
        />
      );
    }
  }

  render() {
    const { loading } = this.state;
    return (
      <Container>
        <Header as="h1" textAlign={'center'} style={{ paddingTop: '1em' }}>
          Mail Query
        </Header>
        <Input
          loading={loading}
          icon="search"
          onChange={this.onInputChange}
          size="large"
          fluid={true}
          placeholder="Search mails..."
        />
        {this.renderMessage()}
        <Segment loading={this.state.loading}>{this.renderMailList()}</Segment>
      </Container>
    );
  }
}

export default App;
