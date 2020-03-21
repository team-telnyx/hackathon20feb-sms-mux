import React from "react";
import PropTypes from "prop-types";
import moment from "moment";
import styled from "styled-components";

import { List, Button } from "antd";
import floridaManService from "../../services/floridaMan";
import { formatPhoneNumber } from "../../utils";

const Message = styled.div`
  font-size: 22px;
  font-weight: bold;
`;

const Messages = () => {
  const [messages, setMessages] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    getMessages();
  }, []);

  function getMessages() {
    setIsLoading(true);
    floridaManService
      .getMessages()
      .then(messages => {
        setMessages(messages.body || []);
        setIsLoading(false);
      })
      .catch(console.error);
  }

  return (
    <div>
      <h2>
        Message Log{" "}
        <Button
          size="small"
          type="primary"
          onClick={getMessages}
          loading={isLoading}
          icon="reload"
        />
      </h2>
      <List
        size="small"
        bordered
        dataSource={messages}
        renderItem={message => (
          <List.Item>
            <div>
              <small>
                <strong>
                  {message.direction === "out"
                    ? formatPhoneNumber(message.teammate_tn)
                    : formatPhoneNumber(message.customer_tn)}
                </strong>{" "}
                ({moment(message.created).format("h:mm a - MMM Do YYYY")})
              </small>
              <Message>{message.text}</Message>
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};

Messages.propTypes = {};

export default Messages;
