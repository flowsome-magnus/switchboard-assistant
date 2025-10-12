# SIP Setup Guide for Switchboard Assistant

This guide covers setting up Twilio SIP trunking and LiveKit SIP integration for the switchboard assistant using **direct SIP trunk connection** (no webhooks needed for basic call routing).

## Prerequisites

- Twilio account with SIP trunking enabled
- LiveKit Cloud account or self-hosted LiveKit server
- Public IP address for SIP signaling
- (Optional) Domain with SSL certificate for webhooks (only needed for advanced features)

## 1. Twilio Configuration

### 1.1 Create SIP Trunk

1. Log into your Twilio Console
2. Go to **Elastic SIP Trunking** > **Trunks**
3. Click **Create Trunk**
4. Configure the trunk:
   - **Friendly Name**: `LiveKit Switchboard SIP Trunk`
   - **Domain Name**: `your-trunk-name.pstn.twilio.com`
   - (No webhook URLs needed for direct SIP connection)

### 1.2 Configure Phone Number

1. Go to **Phone Numbers** > **Manage** > **Active Numbers**
2. Select your phone number
3. Associate with your SIP trunk (no webhook URLs needed for direct SIP)

### 1.3 Set Up SIP Credentials

1. Go to **Elastic SIP Trunking** > **Credentials**
2. Create new credential list:
   - **Friendly Name**: `LiveKit SIP Credentials`
3. Add credentials:
   - **Username**: `livekit-sip-user`
   - **Password**: Generate strong password
4. Associate credential list with your SIP trunk

### 1.4 Configure Origination URIs

1. Go to your SIP trunk settings
2. Add **Origination URI**:
   - **SIP URI**: `sip:your-livekit-sip-endpoint` (e.g., `sip:vjnxecm0tjk.sip.livekit.cloud`)
   - **Priority**: `1`
   - **Weight**: `1`

## 2. LiveKit SIP Configuration

### 2.1 Enable SIP in LiveKit

1. Log into LiveKit Cloud or access your self-hosted server
2. Go to **Settings** > **SIP**
3. Enable SIP functionality
4. Configure SIP settings:
   - **SIP Domain**: `your-livekit-server.com`
   - **SIP Port**: `5060` (or your configured port)
   - **TLS Port**: `5061`
   - **Authentication**: Enable and configure

### 2.2 Configure SIP Inbound Trunk

1. In LiveKit SIP settings, add **Inbound Trunk**:
   - **Name**: `Twilio Inbound`
   - **SIP URI**: `sip:your-twilio-trunk.sip.twilio.com`
   - **Authentication**: Use Twilio credentials
   - **Dispatch Rules**: Configure routing rules

### 2.3 Configure SIP Outbound Trunk

1. Add **Outbound Trunk**:
   - **Name**: `Twilio Outbound`
   - **SIP URI**: `sip:your-twilio-trunk.sip.twilio.com`
   - **Authentication**: Use Twilio credentials
   - **Default Route**: Enable for outbound calls

## 3. Call Flow with Direct SIP Trunk

### 3.1 Inbound Call Flow (Simplified)

```
1. Caller dials your Twilio number
   ↓
2. Twilio routes call directly to LiveKit via SIP trunk
   ↓
3. LiveKit automatically creates room and connects caller
   ↓
4. Your switchboard agent joins the room
   ↓
5. Agent greets caller and handles the conversation
```

### 3.2 Warm Transfer Flow

```
1. Agent initiates warm transfer to employee
   ↓
2. Agent leaves caller room, creates consultation room
   ↓
3. Agent calls employee via SIP to consultation room
   ↓
4. Employee consultation (accept/reject/message)
   ↓
5. If accept: Employee transferred to caller room
   ↓
6. Agent returns to caller room, announces transfer
   ↓
7. Agent disconnects, caller and employee connected
```

### 3.3 Benefits of Direct SIP Approach

- ✅ **Simpler setup** - no webhook infrastructure needed
- ✅ **More reliable** - direct SIP connection
- ✅ **Automatic room creation** - LiveKit handles this
- ✅ **Built-in warm transfers** - LiveKit SIP supports this natively
- ✅ **Easier debugging** - fewer moving parts

## 4. Environment Configuration

Update your `.env` file with the following variables:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_SMS_NUMBER=+1234567890
TWILIO_SIP_TRUNK_ID=your_sip_trunk_id

# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-server.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# Optional: Webhook Configuration (only needed for advanced features)
# WEBHOOK_BASE_URL=https://your-domain.com
```

## 5. Optional: Webhook Endpoints (Advanced Features)

**Note**: These webhook endpoints are only needed for advanced features like call logging, SMS handling, or custom call routing. For basic warm transfers, they are not required.

If you want to implement these features, the following webhook endpoints need to be accessible from Twilio:

- `POST /twilio/voice` - Handle incoming voice calls (optional)
- `POST /twilio/voice-fallback` - Fallback for voice calls (optional)
- `POST /twilio/status` - Call status updates (optional)
- `POST /twilio/sms` - Handle incoming SMS (optional)
- `POST /twilio/sms-fallback` - Fallback for SMS (optional)
- `POST /twilio/recording` - Call recording notifications (optional)

## 6. Testing the Setup

### 6.1 Test Inbound Calls

1. Call your Twilio phone number
2. Verify the call is routed directly to LiveKit
3. Check that the agent responds correctly
4. Monitor logs for any errors

### 6.2 Test Warm Transfers

1. Use the agent to initiate a warm transfer
2. Verify the employee receives the call
3. Check that the consultation room is created
4. Test the transfer flow (employee should be moved to caller room)
5. Verify agent disconnects after transfer

### 6.3 Test Message Taking

1. Ask the agent to take a message
2. Verify message is saved to database
3. Check that SMS/email notifications are sent
4. Verify delivery status tracking

## 7. Troubleshooting

### Common Issues

1. **Calls not reaching LiveKit**
   - Check SIP trunk configuration
   - Verify LiveKit SIP is enabled
   - Check firewall settings

2. **Authentication failures**
   - Verify SIP credentials match
   - Check username/password configuration
   - Ensure credentials are properly associated

3. **Webhook timeouts**
   - Check webhook URL accessibility
   - Verify SSL certificate
   - Monitor webhook response times

4. **Audio quality issues**
   - Check codec configuration
   - Verify network connectivity
   - Monitor bandwidth usage

### Debug Commands

```bash
# Check Twilio call logs
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Calls.json" \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN

# Check SIP trunk status
curl -X GET "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/SipTrunks.json" \
  -u $TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN

# Test webhook endpoint
curl -X POST "https://your-domain.com/twilio/voice" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "CallSid=test&From=%2B1234567890&To=%2B0987654321&CallStatus=ringing"
```

## 7. Security Considerations

1. **Use HTTPS** for all webhook endpoints
2. **Validate webhook signatures** from Twilio
3. **Implement rate limiting** on webhook endpoints
4. **Use strong SIP credentials**
5. **Enable TLS** for SIP signaling
6. **Monitor for suspicious activity**

## 8. Monitoring and Logging

1. **Set up monitoring** for webhook endpoints
2. **Log all SIP events** for debugging
3. **Monitor call quality** metrics
4. **Track webhook response times**
5. **Set up alerts** for failures

## 9. Scaling Considerations

1. **Load balancing** for webhook endpoints
2. **Database connection pooling**
3. **Caching** for frequently accessed data
4. **Horizontal scaling** of agent instances
5. **CDN** for static webhook responses

## 10. Backup and Recovery

1. **Backup SIP configuration**
2. **Document all settings**
3. **Test disaster recovery procedures**
4. **Maintain configuration versioning**
5. **Regular testing** of backup systems
