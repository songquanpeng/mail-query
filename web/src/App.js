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
  Checkbox,
  Button,
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
      uploading: false,
      message: {
        visible: false,
        color: 'red',
        header: '',
        content: '',
      },
      searchTypingTimeout: 0,
    };
    this.fileInputRef = React.createRef();
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

  onFileInputChange = (event) => {
    this.setState({ uploading: true });
    let files = event.target.files;
    let form = new FormData();
    for (let i = 0; i < files.length; ++i) {
      form.append(`file-${i}.eml`, files[i]);
    }
    axios
      .post('/upload', form, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then((res) => {
        this.setState({ uploading: false });
        console.log(res);
      })
      .catch((err) => {
        console.error(err);
        this.showMessage('red', 'Failed to upload file', err.toString());
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
        this.setState({ loading: false });
        this.setState({ mails: res.data });
      })
      .catch((err) => {
        console.error(err);
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

  renderOptions() {
    const options = [
      'subject',
      'sender',
      'receiver',
      'date',
      'content',
      'attachment name',
      'attachment content',
    ];
    const items = [];
    for (const [index, value] of options.entries()) {
      items.push(
        <Checkbox
          key={index}
          label={value}
          name={value}
          checked={this.state.options[index]}
          onClick={() => {
            this.clickCheckbox(index);
          }}
          style={{ marginRight: '8px' }}
        />
      );
    }
    return <Container style={{ paddingTop: '8px' }}>{items}</Container>;
  }

  clickCheckbox = (index) => {
    let options = this.state.options;
    options[index] = !options[index];
    this.setState({ options });
  };

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
          onChange={this.onInputChange}
          size="large"
          fluid={true}
          placeholder="Search mails..."
          action
        >
          <input />
          <Button
            animated="vertical"
            onClick={() => {
              this.fileInputRef.current.click();
            }}
          >
            <Button.Content hidden>Upload</Button.Content>
            <Button.Content visible>
              <Icon name="upload" />
            </Button.Content>
          </Button>
        </Input>
        {this.renderOptions()}
        {this.renderMessage()}
        <Segment loading={loading}>{this.renderMailList()}</Segment>
        <input
          ref={this.fileInputRef}
          type="file"
          name="files"
          accept=".eml"
          multiple="multiple"
          onChange={this.onFileInputChange}
          style={{ display: 'none' }}
        />
      </Container>
    );
  }
}

export default App;
