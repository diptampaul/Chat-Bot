import 'package:flutter/material.dart';

SnackBar showMessage(String firstMessage, String message, final bgColor, int d){
  final SnackBar snackBar = SnackBar(
    content: Container(
      padding: const EdgeInsets.fromLTRB(30.0, 20.0, 30.0, 0.0),
      height: 90.0,
      decoration: BoxDecoration(
        borderRadius: const BorderRadius.all(Radius.circular(18.0)),
        color: bgColor,
      ),
      child: Column(
          children: [
            Text(
              firstMessage.toString(),
              style: const TextStyle(
                  fontSize: 18,
                  color: Colors.white,
                  fontWeight: FontWeight.bold
              ),
            ),
            const SizedBox(
              height: 10.0,
            ),
            Text(
              message.toString(),
              style: const TextStyle(
                  fontSize: 12,
                  color: Colors.white,
                  fontWeight: FontWeight.bold
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ]
      ),
    ),
    behavior: SnackBarBehavior.floating,
    backgroundColor: Colors.transparent,
    elevation: 0.0,
    duration: Duration(seconds: d),
  );
  return snackBar;
}